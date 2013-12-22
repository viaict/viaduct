''''
Python library for Mollie iDeal implementation
Written by Dave de Fijter - Indentity - http://www.indentity.nl
Version 0.0.1
'''

import urllib
import urllib2
from lxml import objectify

class IDealResponseError(AttributeError):
    '''
    This error is raised when the response is not the expected response
    '''
    pass

class IDeal:
    '''
    IDeal implementation class for Mollie payment services
    Written by Dave de Fijter - Indentity - http://www.indentity.nl
    Version 0.0.1

    Basic usage:

    To get the list of banks:

        from mollie.ideal import IDeal
        ideal = IDeal(partner_id=000000, testmode=False)
        banks = ideal.banklist()

    To start a transaction and get the URL to redirect the customer to:

        from mollie.ideal import IDeal
        ideal = IDeal(partner_id=000000, testmode=False)
        transaction = ideal.transaction(amount=120.0, bank_id=9999,
        description='cake for Dave', report_url =
        'http://www.example.com/ideal/check/',
        return_url = 'http://www.example.com/returned/')
        url = transaction['url']

    To check if the transaction has been completed (replace the request.get if
    you are using something else as Django):

        transaction_id = request.GET.get('transaction_id')
        ideal = IDeal(partner_id=000000, testmode=False)
        check = ideal.check(transaction_id)
        payed = check['payed']

    You can handle XML exceptions like this if you wish:

        from mollie.ideal import IDealResponseError, IDeal
        ideal = IDeal(partner_id=000000)
        try:
            ideal.banklist()
        except IDealResponseError, e:
            print 'Your error handling here!'

    That's all, have fun!

    Here is a unittest to check if this all still works as it should;
    Execute this file from the commandline and it should give no output if
    everything is correct, errors otherwise.

    Please change the 000000 to your own partner ID and switch on test mode
    in your account to try out the unit test.

    >>> ideal = IDeal(partner_id=1238121, testmode=True)
    >>> banks = ideal.banklist()
    >>> print banks
    [('9999', 'TBM Bank')]
    >>> t = ideal.transaction(80.0, banks[0][0], 'testtransaction', 'http://www.example.com/ideal/check/', 'http://www.example.com/ideal/done/')
    >>> print t['amount']
    80.0
    >>> c = ideal.check(t['transaction_id'])
    >>> print c['payed']
    False
    >>> t = ideal.transaction(20.0, banks[0][0], 'testtransaction', 'http://www.example.com/ideal/check/', 'http://www.example.com/ideal/done/')
    >>> accept_url = '%spayed=true' % t['url'].split('trxid=')[0]
    >>> import urllib2, time
    >>> resp = urllib2.urlopen(accept_url).read()
    >>> time.sleep(2)
    >>> c = ideal.check(t['transaction_id'])
    >>> print c['payed']
    True
    '''

    def __init__(self, partner_id, testmode=False,
        api_url='https://secure.mollie.nl/xml/ideal'):
        '''
        A partner_id is the only mandatory attribute, you can find this in your Mollie account overview
        '''
        self.testmode = bool(testmode)
        self.api_url = api_url
        self.partner_id = partner_id

    def _get_response(self, params):
        '''
        This private function is used internally for handling XML responses from Mollie
        '''
        if self.testmode:
            params['testmode'] = 'true'
        url = '%s?%s' % (self.api_url, urllib.urlencode(params))
        fhandle = urllib2.urlopen(url)
        data = objectify.parse(fhandle)
        errors = data.xpath('item[@type="error"]')
        if errors:
            raise IDealResponseError, ([x.message for x in errors], url)
        return data.getroot()

    def banklist(self):
        '''
        Returns a list of all banks, contains tuples with bank_id and bank_name
        '''
        banklist = self._get_response({'a': 'banklist'})
        return [(bank.bank_id.text, bank.bank_name) for bank in banklist.bank]

    def transaction(self, amount, bank_id, description,
        report_url, return_url, profile_key=None):
        '''
        Start a transaction and return the transaction ID, Amount and URL if it's accepted

        Parameters:
         - amount: The amount in EUR, for example: 40.0 or 40, this is NOT the amount in cents as requested by Mollie but in EUR.
         - bank_id: The ID of the selected bank that handles the transaction
         - description: a short description (max. 29 chars) of the product people are paying for
         - report_url: The callback url of the transaction
         - return_url: The URL of the page the user is transfered back
           to after the transaction
         - profile_key: The mollie profile key if there are multiple profiles,
           can be found in the mollie profile overview

        Returns a dictionary with the keys 'url', 'transaction_id',
        'amount' and 'currency'
        '''
        cents = int(amount * 100)
        params = {
            'a':            'fetch',
            'partnerid':    self.partner_id,
            'amount':       cents,
            'bank_id':      bank_id,
            'description':  description,
            'reporturl':    report_url,
            'returnurl':    return_url,
        }
        if profile_key:
            params['profile_key'] = profile_key
        resp = self._get_response(params)
        return {
            'url': unicode(resp.order.URL),
            'transaction_id': unicode(resp.order.transaction_id),
            'amount': float(resp.order.amount) / 100.0,
            'currency': unicode(resp.order.currency),
        }

    def check(self, transaction_id):
        '''
        Check if the transaction has been payed
        Only the first check will give a Payed = True result

        returns a dictionary with the keys 'payed', 'transaction_id', 'amount'
        (float in EUR, not cents), 'currency' and consumer_* if available.
        '''
        params = {
            'a': 'check',
            'partnerid': self.partner_id,
            'transaction_id': transaction_id,
        }
        resp = self._get_response(params)
        data = {
            'payed': bool(resp.order.payed),
            'transaction_id': unicode(resp.order.transaction_id),
            'amount': float(resp.order.amount) / 100.0,
            'currency': unicode(resp.order.currency),
        }

        if hasattr(resp.order, 'consumer'):
            data['consumer_name'] = unicode(resp.order.consumer.consumerName),
            data['consumer_account'] = \
                unicode(resp.order.consumer.consumerAccount),
            data['consumer_city'] = unicode(resp.order.consumer.consumerCity),
        else:
            data['consumer_name'] = data['consumer_account'] = \
            data['consumer_city'] = None

        return data

if __name__ == "__main__":
    import doctest
    doctest.testmod()
