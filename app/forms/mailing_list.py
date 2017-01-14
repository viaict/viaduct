from flask_wtf import Form
from wtforms import BooleanField, HiddenField, FieldList, FormField


class MailingListEntryForm(Form):
    mailing_list_name = HiddenField()
    mailing_list_id = HiddenField()
    subscribed = BooleanField()


class MailingListForm(Form):
    subscriptions = FieldList(FormField(MailingListEntryForm), min_entries=1)
