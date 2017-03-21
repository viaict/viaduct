from flask_wtf import Form

from wtforms import BooleanField, FormField, FieldList, SubmitField, \
    SelectField, StringField

from wtforms.validators import InputRequired

from wtforms import Form as UnsafeForm


class ViewGroupEntry(UnsafeForm):
    select = BooleanField(None)


class ViewGroupForm(Form):
    entries = FieldList(FormField(ViewGroupEntry))
    delete_group = SubmitField('Verwijder groep')


class EditGroupPermissionEntry(UnsafeForm):
    select = SelectField(None, coerce=int, choices=[(0, "Geen"), (1, "Lees"),
                                                    (2, "Lees/Schrijf")])


class EditGroup(Form):
    name = StringField('Naam', validators=[
        InputRequired(message='Geen naam opgegeven')])
    maillist = StringField('Naam maillijst')


class CreateGroup(EditGroup):
    committee_url = StringField('Commissie-pagina URL (zonder slash)')


class EditGroupPermissionForm(Form):
    permissions = FieldList(FormField(EditGroupPermissionEntry))
    add_module_name = SelectField('Module')
    add_module_permission = SelectField(None, coerce=int,
                                        choices=[(0, "Geen"), (1, "Lees"),
                                                 (2, "Lees/Schrijf")])
    save_changes = SubmitField('Sla veranderingen op')
