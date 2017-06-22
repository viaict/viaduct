from flask_babel import _
from flask_wtf import Form
from wtforms import StringField, DateField, SelectField, FormField, \
    FieldList, Form as UnsafeForm
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired

from app.models import Activity, User
from app.models.alv import AlvPresidium


class AlvPresidiumFormEntry(UnsafeForm):
    user = QuerySelectField(_('User'), query_factory=lambda: User.query,
                            allow_blank=False)

    role = SelectField(_('Presidium role'),
                       choices=AlvPresidium.presidium_roles)


class AlvForm(Form):
    nl_name = StringField(_('Dutch name'), validators=[InputRequired()])
    en_name = StringField(_('English name'), validators=[InputRequired()])

    date = DateField(_('Date'))

    activity = QuerySelectField(_('Activity'),
                                query_factory=lambda: Activity.query,
                                allow_blank=False)

    presidium = FieldList(FormField(AlvPresidiumFormEntry, label=_(
        'Presidium'), min_entries=3))
