from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import Form as UnsafeForm
from wtforms import FormField, FieldList, SubmitField, \
    StringField, SelectMultipleField, SelectField
from wtforms.validators import InputRequired, StopValidation

from app import Roles
from app.forms.fields import EmailListField


class EditGroupPermissionEntry(UnsafeForm):
    select = SelectField(None, coerce=int, choices=[(0, "Geen"), (1, "Lees"),
                                                    (2, "Lees/Schrijf")])


illegal_prefixes = ['list-', 'coordinator-']


def validate_maillist(form, field):
    data_strip = field.data.strip()
    if data_strip == '':
        # Remove any previous errors
        field.errors[:] = []

        # Stop the validation, either with
        # a message that the input is required or without one
        # if it is not required
        if form.mailtype.data == 'none':
            raise StopValidation()
        else:
            raise StopValidation(field.gettext('This field is required.'))
    else:
        if any(data_strip.startswith(p) for p in illegal_prefixes):
            raise StopValidation("{}: {}".format(
                _('E-mail address cannot start with any of the following'),
                ', '.join(illegal_prefixes)))


class EditGroupForm(FlaskForm):
    name = StringField('Naam', validators=[InputRequired()])
    mailtype = SelectField(_('E-mail type'), choices=[
        ('none', _('None')), ('mailinglist', _('Mailing list')),
        ('mailbox', 'Mail box')])
    maillist = EmailListField(_('E-mail address'),
                              validators=[validate_maillist])


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
