from flask_wtf import Form

from wtforms import BooleanField, FormField, FieldList, SubmitField, \
    SelectField

from wtforms import Form as UnsafeForm


class ViewGroupEntry(UnsafeForm):
    select = BooleanField(None)


class ViewGroupForm(Form):
    entries = FieldList(FormField(ViewGroupEntry))
    delete_group = SubmitField('Delete group')


class EditGroupPermissionEntry(UnsafeForm):
    select = SelectField(None, coerce=int, choices=[(0, "Geen"), (1, "Lees"),
                                                    (2, "Lees/Schrijf")])


class EditGroupPermissionForm(Form):
    permissions = FieldList(FormField(EditGroupPermissionEntry))
    add_module_name = SelectField('Module')
    add_module_permission = SelectField(None, coerce=int,
                                        choices=[(0, "Geen"), (1, "Lees"),
                                                 (2, "Lees/Schrijf")])
    save_changes = SubmitField('Sla veranderingen op')
