from flask_wtf import Form
from flask_babel import lazy_gettext as _
from wtforms import BooleanField, HiddenField, FieldList,\
    FormField, StringField
from wtforms.validators import InputRequired, Email


class MailingListEntryForm(Form):
    mailing_list_name = HiddenField()
    mailing_list_id = HiddenField()
    subscribed = BooleanField()


class MailingListForm(Form):
    subscriptions = FieldList(FormField(MailingListEntryForm), min_entries=0)


class AnonymousMailingListForm(Form):
    email = StringField(_('E-mail adress'), validators=[
        InputRequired(message=_('No e-mail adress submitted')),
        Email(message=_('Invalid e-mail adress submitted'))])
    subscriptions = FieldList(FormField(MailingListEntryForm), min_entries=0)
