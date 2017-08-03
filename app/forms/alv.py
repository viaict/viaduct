from flask_babel import _
from flask_wtf import Form
from wtforms import StringField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired

from app.models import Activity
from app.service import user_service


class AlvForm(Form):
    nl_name = StringField(_('Dutch name'), validators=[InputRequired()])
    en_name = StringField(_('English name'), validators=[InputRequired()])

    date = DateField(_('Date'))

    activity = QuerySelectField(
        _('Activity'),
        query_factory=lambda: Activity.query)
    chairman = QuerySelectField(
        _('Chairman'),
        query_factory=lambda: user_service.find_members())
    secretary = QuerySelectField(
        _('Secretary'),
        query_factory=lambda: user_service.find_members())
