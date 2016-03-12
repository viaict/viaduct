# coding: utf-8
from wtforms import TextAreaField, SelectField, BooleanField
from flask.ext.babel import lazy_gettext as _
from viaduct.forms.page import SuperPageForm


class CommitteeForm(SuperPageForm):
    nl_description = TextAreaField(_('Description'))
    en_description = TextAreaField(_('Description'))
    group_id = SelectField(_('Group'), coerce=int)
    coordinator_id = SelectField(_('Coördinator'), coerce=int)
    interim = BooleanField(_('Interim coördinator'))

    # Override validate from the Form class
    def validate(self):

        # Validate all other fields with default validators
        if not SuperPageForm.validate(self):
            return False

        # Test if either english or dutch is entered
        result = True
        if not (self.nl_title.data or self.en_title.data):
            self.nl_title.errors.append(
                _('Either Dutch or English title required'))
            result = False
        if not (self.nl_description.data or self.en_description.data):
            self.nl_description.errors.append(
                _('Either Dutch or English description required'))
            result = False

        # XOR the results to test if both of a language was given
        if bool(self.nl_title.data) != bool(self.nl_description.data):
            self.nl_title.errors.append(
                _('Dutch title requires Dutch description and vice versa'))
            result = False
        if bool(self.en_title.data) != bool(self.en_description.data):
            self.en_title.errors.append(
                _('English title requires English description and vice versa'))
            result = False

        return result
