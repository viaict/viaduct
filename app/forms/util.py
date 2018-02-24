import inspect
import itertools

from wtforms import RadioField, SubmitField, SelectFieldBase

from app.forms.fields import CustomFormSelectField, \
    OrderedSelectMultipleField, OrderedQuerySelectMultipleField


class FieldTabGroup:
    """Represents a group of fields divided into tabs."""

    def __init__(self, tabs):
        """Tabs should be a list of FieldTabs."""

        self.type = self.__class__.__name__
        self.tabs = tabs

        # Don't allow empty tabs
        if len(tabs) == 0:
            raise ValueError('Tabs are empty')

        # Check if all tabs are FieldTab
        if not all(isinstance(t, FieldTab) for t in tabs):
            raise ValueError('Tabs should all be instances of FieldTab')

        # First field is used to determine the place of the tab group
        self._firstfield = tabs[0].field_names[0]

        # Make a list of all fieldnames
        self._fieldnames = []
        for tab in self.tabs:
            self._fieldnames.extend(tab.field_names)

    def _set_form(self, form):
        """
        Pass the form to the FieldTabGroup.

        Internal method used by FormWrapper.
        """
        self.form = form

        # Build a list of (tabname, fieldlist) tuples,
        # where fieldlist contains the field objects itself,
        # which is why the form object is required
        self._tab_fields = []
        for tab in self.tabs:
            fields = []
            for field_name in tab.field_names:
                fields.append(getattr(form, field_name))
            self._tab_fields.append((tab.name, fields))

    def __iter__(self):
        if not hasattr(self, 'form'):
            raise ValueError('_set_form should be called before iterating')
        return iter(self._tab_fields)

    @property
    def hex_id(self):
        """Get the id of the object as hexadecimals. (used for rendering)."""
        return hex(id(self))[2:]


class FieldTab:
    """
    Represents a tab containing fields.

    To be used in combination with FieldTabGroup.
    """

    def __init__(self, name, field_names):
        if len(field_names) == 0:
            raise ValueError('Fields are empty')
        self.name = name
        self.field_names = field_names

    def __repr__(self):
        return "<{} '{}'>".format(self.__class__.__name, self.name)


class FieldVerticalSplit:
    """
    Vertical field splits.

    Represents a vertical split of fields,
    i.e. fields next to each other.
    """

    def __init__(self, field_names, large_spacing=False):
        """
        field_names should be a list of list of fields to be splitted.

        For example,
            [['X1', 'X2'], ['Y1', 'Y2']]
        will render as:
            [   X1   ]  [   Y1   ]
            [   X2   ]  [   Y2   ]
        """
        self.amount_splits = len(field_names)
        self.type = self.__class__.__name__

        # Allowed amounts of splits which all can be divided evenly
        allowed_split_amounts = [2, 3, 4]

        if self.amount_splits not in allowed_split_amounts:
            raise ValueError("Amount of splits should be equal to one of: {}",
                             ", ".join(map(str, allowed_split_amounts)))

        self.field_names_list = field_names

        # Make a list of all fieldnames (i.e. flatten the field_names list)
        self._fieldnames = []
        for fields in self.field_names_list:
            self._fieldnames.extend(fields)

        # First field is used to determine the place of the vertical split
        self._firstfield = field_names[0][0]

        if large_spacing:
            if self.amount_splits == 2:
                self.column_sizes = [5, 5]
                self.spacing_sizes = [0, 2]
            elif self.amount_splits == 3:
                self.column_sizes = [3, 4, 3]
                self.spacing_sizes = [0, 1, 1]
            elif self.amount_splits == 4:
                self.column_sizes = [2, 2, 2, 2]
                self.spacing_sizes = [0, 1, 2, 1]
        else:
            self.column_sizes = [12 // self.amount_splits] * self.amount_splits
            self.spacing_sizes = [0] * self.amount_splits

    def _set_form(self, form):
        """
        Pass the form to the FieldVerticalSplit.

        Internal method used by FormWrapper.
        """
        self.form = form

        self._fields = []
        for field_names in self.field_names_list:
            fields = []
            for field_name in field_names:
                fields.append(getattr(form, field_name))
            self._fields.append(fields)

    def __iter__(self):
        if not hasattr(self, 'form'):
            raise ValueError('_set_form should be called before iterating')
        return iter(self._fields)


class FormWrapper:
    """Helper class for form rendering."""

    def __init__(self, form):
        self.form = form
        self.groups = []
        self.vsplits = []
        self.ordered_multiselect_fields = []

        self.csrf_token = form.csrf_token

        self.has_ordered_multiselect_fields = False
        self.has_select_fields = False
        self.has_custom_form_fields = False
        self.has_submit_field = False

        for attrname, obj in inspect.getmembers(form):
            # Collect the tab groups in the form
            if isinstance(obj, FieldTabGroup):
                obj.name = attrname
                self.groups.append(obj)

            # Collect the vertical splits in the form
            elif isinstance(obj, FieldVerticalSplit):
                obj.name = attrname
                self.vsplits.append(obj)

            # Check if the form has select fields
            elif isinstance(obj, SelectFieldBase) \
                    and not isinstance(obj, OrderedSelectMultipleField) \
                    and not isinstance(obj, OrderedQuerySelectMultipleField) \
                    and not isinstance(obj, RadioField):
                self.has_select_fields = True

            # Check if the form has ordered multi-select fields
            elif isinstance(obj, OrderedSelectMultipleField) \
                    or isinstance(obj, OrderedQuerySelectMultipleField):
                self.has_ordered_multiselect_fields = True
                self.ordered_multiselect_fields.append(obj)

            # Check if the form has custom form select fields
            elif isinstance(obj, CustomFormSelectField):
                self.has_select_fields = True
                self.has_custom_form_fields = True

            # Check if the form has a submit field
            elif isinstance(obj, SubmitField):
                self.has_submit_field = True

        try:
            # Dictionary from first field object of a tab group
            # to the group object itself
            groups_firstfields = {
                getattr(form, g._firstfield): g
                for g in self.groups
            }

            # List of all fields belonging to a group
            groups_fields = list(map(
                lambda f: getattr(form, f), itertools.chain(
                    *map(lambda g: g._fieldnames, self.groups))))
        except TypeError:
            raise TypeError('Group field should be a string')

        try:
            # Dictionary from first field object of a vertial split
            # to the vertical split object itself
            vsplits_firstfields = {
                getattr(form, v._firstfield): v
                for v in self.vsplits
            }

            # List of all fields belonging to a vertical split
            vsplit_fields = list(map(
                lambda f: getattr(form, f), itertools.chain(
                    *map(lambda v: v._fieldnames, self.vsplits))))
        except TypeError:
            raise TypeError('Vertical split field should be a string')

        self._fields = []

        ignore_fields = []

        if hasattr(form, '_RenderIgnoreFields'):
            ignore_fields = form._RenderIgnoreFields

        for field in form:
            # Add the group when the first field occurs in the field list
            if field in groups_firstfields:
                self._fields.append(groups_firstfields[field])

            # Add the vertical split when the first field
            # occurs in the field list
            elif field in vsplits_firstfields:
                self._fields.append(vsplits_firstfields[field])

            # Otherwise, add a field when it does not belong to a group
            elif (field not in groups_fields and
                  field not in vsplit_fields and
                  field.name not in ignore_fields):
                self._fields.append(field)

        # Give every group and vsplit the form object to make them
        # iterable over their tabs/fields
        for g in self.groups + self.vsplits:
            g._set_form(form)

    def __iter__(self):
        return iter(self._fields)
