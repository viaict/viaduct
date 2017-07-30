from flask_babel import _
from flask_wtf import Form
from wtforms import StringField, DateField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired

from app.forms.util import FieldVerticalSplit
from app.models import Activity
from app.service import user_service


class AlvForm(Form):
    nl_name = StringField(_('Dutch name'), validators=[InputRequired()])
    en_name = StringField(_('English name'), validators=[InputRequired()])

    date = DateField(_('Date'))

    activity = QuerySelectField(_('Activity'),
                                query_factory=lambda: Activity.query,
                                allow_blank=False)

    presidium_chairman = SelectField(_('Presidium chairman'), coerce=int)
    presidium_secretary = SelectField(_('Presidium secretary'), coerce=int)
    presidium_other = SelectField(_('Presidium other'), coerce=int)

    presidium = FieldVerticalSplit(
        [['presidium_chairman'], ['presidium_secretary'], ['presidium_other']]
    )

    @classmethod
    def from_alv(cls, request_form, alv=None):
        form = cls(request_form, obj=alv)
        user_choices = [(u.id, u.name) for u in user_service.find_members()]
        user_choices.insert(0, (0, ""))
        form.presidium_chairman.choices = user_choices
        form.presidium_secretary.choices = user_choices
        form.presidium_other.choices = user_choices
        return form
