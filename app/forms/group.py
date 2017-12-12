from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField, FormField, FieldList, SubmitField, \
    StringField, SelectMultipleField, SelectField
from wtforms import Form as UnsafeForm
from wtforms.validators import InputRequired

from app import Roles
from app.forms.fields import EmailListField


class ViewGroupEntry(UnsafeForm):
    select = BooleanField(None)


class ViewGroupForm(FlaskForm):
    entries = FieldList(FormField(ViewGroupEntry))
    delete_group = SubmitField('Verwijder groep')


class EditGroupPermissionEntry(UnsafeForm):
    select = SelectField(None, coerce=int, choices=[(0, "Geen"), (1, "Lees"),
                                                    (2, "Lees/Schrijf")])


class EditGroupForm(FlaskForm):
    name = StringField('Naam', validators=[InputRequired()])
    maillist = EmailListField('Naam maillijst')


class CreateGroupForm(EditGroupForm):
    committee_url = StringField('Commissie-pagina URL (zonder slash)')


class GroupRolesForm(FlaskForm):
    roles = SelectMultipleField(_("Roles"), choices=Roles.choices(),
                                coerce=Roles.coerce)


class EditGroupPermissionForm(FlaskForm):
    permissions = FieldList(FormField(EditGroupPermissionEntry))
    add_module_name = SelectField('Module')
    add_module_permission = SelectField(None, coerce=int,
                                        choices=[(0, "Geen"), (1, "Lees"),
                                                 (2, "Lees/Schrijf")])
    save_changes = SubmitField('Sla veranderingen op')
