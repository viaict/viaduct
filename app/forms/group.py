from flask_babel import lazy_gettext as _
from flask_wtf import Form
from wtforms import BooleanField, FormField, FieldList, SubmitField, \
    StringField, SelectMultipleField
from wtforms import Form as UnsafeForm
from wtforms.validators import InputRequired

from app import Roles


class ViewGroupEntry(UnsafeForm):
    select = BooleanField(None)


class ViewGroupForm(Form):
    entries = FieldList(FormField(ViewGroupEntry))
    delete_group = SubmitField('Verwijder groep')


class EditGroup(Form):
    name = StringField('Naam', validators=[
        InputRequired(message='Geen naam opgegeven')])
    maillist = StringField('Naam maillijst')


class CreateGroup(EditGroup):
    committee_url = StringField('Commissie-pagina URL (zonder slash)')


# FIXME Flask_form
class GroupRolesForm(Form):
    roles = SelectMultipleField(_("Roles"), choices=Roles.choices(),
                                coerce=Roles.coerce)
