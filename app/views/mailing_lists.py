from flask import redirect, render_template, request, Blueprint, url_for
from flask_login import current_user

from app import db
from app.forms.mailing_list import MailingListForm
from app.models.mailing_lists import MailingList, MailingListUser
from app.models.user import User

blueprint = Blueprint('mailings', __name__, url_prefix='/mailings')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:user_id>/', methods=['GET', 'POST'])
def view():
    if current_user is User.get_anonymous_user():
        return redirect(url_for('mailing_lists.anonymous'))
    else:
        subscriptions = []
        for mailinglist in MailingList.query.all():
            print(mailinglist.name)
            subscription = mailinglist.followers.\
                filter(MailingListUser.user_id == current_user.id).first()
            if subscription:
                subscriptions.append({"mailing_list_name": mailinglist.name,
                                      "mailing_list_id": mailinglist.id,
                                      "subscribed": subscription.subscribed})
            else:
                subscriptions.append({"mailing_list_name": mailinglist.name,
                                      "mailing_list_id": mailinglist.id,
                                      "subscribed": False})
        form = MailingListForm(request.form, subscriptions=subscriptions)
        if form.validate_on_submit():
            for subscription in form.subscriptions.data:
                relation = MailingListUser.query.\
                    filter(MailingListUser.mailing_list_id ==
                           int(subscription['mailing_list_id']),
                           MailingListUser.user_id == current_user.id).first()
                if relation:
                    relation.subscribed = subscription['subscribed']
                elif subscription['subscribed'] is True:
                    relation = MailingListUser(current_user.id,
                                               subscription['mailing_list_id'],
                                               True)
                    db.session.add(relation)
                db.session.commit()
        return render_template('mailinglist/view_user.htm',
                               form=form)


@blueprint.route('/all', methods=['GET', 'POST'])
def anonymous():
    if current_user is User.get_anonymous_user():
        mailing_lists = MailingList.query.\
            filter(MailingList.member_only is False).all()
        subscriptions = []
        for mailinglist in mailing_lists:
            subscriptions.append({"mailing_list_name": mailinglist.name,
                                  "mailing_list_id": mailinglist.id,
                                  "subscribed": False})
        form = MailingListForm(request.form, subscriptions=subscriptions)
        if form.validate_on_submit():
            for subscription in form.subscriptions.data:
                if subscription['subscribed'] is True:
                    pass
        return render_template('mailinglist/view_public.htm',
                               mailing_lists=mailing_lists)
    else:
        return redirect(url_for('mailing_lists.view'))
