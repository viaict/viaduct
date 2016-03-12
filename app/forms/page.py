from flask_wtf import Form
from wtforms import BooleanField, StringField, TextAreaField, FieldList, \
    SelectField, SubmitField, RadioField, FormField

from wtforms.validators import InputRequired, Regexp, Optional

from wtforms import Form as UnsafeForm
from flask.ext.babel import lazy_gettext as _


class EditGroupPagePermissionEntry(UnsafeForm):
    select = SelectField(None, coerce=int, choices=[
        (0, _('None')), (1, _('Read')), (2, _('Read/Write'))])


class SuperPageForm(Form):
    """TODO"""
    nl_title = StringField(_('Dutch title'))
    en_title = StringField(_('English title'))

    comment = StringField(_('Comment for change'), [Optional()])
    needs_payed = BooleanField(_('Visible for members only'))


class PageForm(SuperPageForm):
    nl_content = TextAreaField(_('Dutch content'))
    en_content = TextAreaField(_('English content'))
    filter_html = BooleanField(_('Do not filter HTML tags'))
    custom_form_id = SelectField(_('Custom form'), coerce=int)
    permissions = FieldList(FormField(EditGroupPagePermissionEntry))

    def validate(self):

        # Validate all other fields with default validators
        if not SuperPageForm.validate(self):
            return False
        result = True

        # Test if either english or dutch is entered
        result = True
        if not (self.nl_title.data or self.en_title.data):
            self.nl_title.errors.append(
                _('Either Dutch or English title required'))
            result = False
        if not (self.nl_content.data or self.en_content.data):
            self.nl_content.errors.append(
                _('Either Dutch or English content required'))
            result = False

        # XOR the results to test if both of a language was given
        if bool(self.nl_title.data) != bool(self.nl_content.data):
            self.nl_title.errors.append(
                _('Dutch title requires Dutch content and vice versa'))
            result = False
        if bool(self.en_title.data) != bool(self.en_content.data):
            self.en_title.errors.append(
                _('English title requires English content and vice versa'))
            result = False

        return result


class HistoryPageForm(Form):
    previous = RadioField(_('Previous'), coerce=int)
    current = RadioField(_('Current'), coerce=int)
    compare = SubmitField(_('Compare'))


# TODO: This is not used anywhere...
class ChangePathForm(Form):
    path = StringField('Path', [InputRequired(),
                                Regexp(r'^ */?[\w-]+(/[\w-]+)*/? *$',
                                       message='You suck at typing '
                                       'URL paths')])
    move_only_this = SubmitField('Only this page')
    move_children = SubmitField('This and its children ')
