from wtforms import SelectField, RadioField
import inspect
import itertools

from app.forms.fields import CustomFormSelectField


class FieldTabGroup:
    def __init__(self, groups):
        self.type = self.__class__.__name__
        self.groups = groups
        try:
            self._firstfield = groups[0][1][0]
        except IndexError:
            raise ValueError('Groups are malformed or do not contain field')

        self._fieldnames = []

        for group_name, group_fields in self.groups:
            self._fieldnames.extend(group_fields)

    def _set_form(self, form):
        self.form = form
        self._group_fields = []
        for (name, field_names) in self.groups:
            fields = []
            for field_name in field_names:
                fields.append(getattr(form, field_name))
            self._group_fields.append((name, fields))

    def __iter__(self):
        if not hasattr(self, 'form'):
            raise ValueError('_set_form should be called before iterating')
        return iter(self._group_fields)

    @property
    def hex_id(self):
        return hex(id(self))[2:]


class FormWrapper:
    def __init__(self, form):
        self.form = form
        self.groups = []
        self.has_select_fields = False
        self.has_custom_form_fields = False
        for attrname, obj in inspect.getmembers(form):
            if isinstance(obj, FieldTabGroup):
                self.groups.append(obj)
            elif isinstance(obj, SelectField) \
                    and not isinstance(obj, RadioField):
                self.has_select_fields = True
            elif isinstance(obj, CustomFormSelectField):
                self.has_select_fields = True
                self.has_custom_form_fields = True

        self.has_groups = len(self.groups) > 0
        form_fields = list(form)

        try:
            # Dictionary from first field of a group to the group itself
            groups_firstfields = {
                getattr(form, g._firstfield): g
                for g in self.groups
            }

            # List of the names of all fields belonging to a group
            groups_fields = list(map(
                lambda f: getattr(form, f), itertools.chain(
                    *map(lambda g: g._fieldnames, self.groups))))
        except TypeError:
            raise TypeError('Group field should be a string')

        self._fields = []

        for field in form_fields:
            # Add the group when the first field occurs in the field list
            if field in groups_firstfields:
                self._fields.append(groups_firstfields[field])
            # Otherwise, add a field when it does not belong to a group
            elif field not in groups_fields:
                self._fields.append(field)

        for g in self.groups:
            g._set_form(form)

    def __iter__(self):
        return iter(self._fields)
