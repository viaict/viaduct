from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, TextAreaField, SelectField, \
    SubmitField, RadioField, IntegerField
from wtforms import Form as UnsafeForm
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import InputRequired, Regexp, Optional

from app.forms.fields import CustomFormSelectField
from app.service import group_service


class EditGroupPagePermissionEntry(UnsafeForm):
    select = SelectField(None, coerce=int, choices=[
        (0, _('None')), (1, _('Read')), (2, _('Read/Write'))])


class SuperPageForm(FlaskForm):
    """TODO."""

    nl_title = StringField(_('Dutch title'))
    en_title = StringField(_('English title'))

    comment = StringField(_('Comment for change'), [Optional()])


class PageForm(SuperPageForm):
    nl_content = TextAreaField(_('Dutch content'))
    en_content = TextAreaField(_('English content'))
    filter_html = BooleanField(_('Do not filter HTML tags'))
    custom_form_id = IntegerField()

    read_groups = QuerySelectMultipleField(
        _("Groups with read permission"),
        query_factory=lambda: group_service.find_groups(),
        get_label='name')
    write_groups = QuerySelectMultipleField(
        _("Groups with write permission"),
        query_factory=lambda: group_service.find_groups(),
        get_label='name')

    needs_paid = BooleanField(_('Visible for members only'))
    custom_form_id = CustomFormSelectField(_('Form'))

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


class HistoryPageForm(FlaskForm):
    previous = RadioField(_('Previous'), coerce=int)
    current = RadioField(_('Current'), coerce=int)
    compare = SubmitField(_('Compare'))


# TODO: This is not used anywhere...
class ChangePathForm(FlaskForm):
    path = StringField('Path', [InputRequired(),
                                Regexp(r'^ */?[\w-]+(/[\w-]+)*/? *$',
                                       message='You suck at typing '
                                       'URL paths')])
    move_only_this = SubmitField('Only this page')
    move_children = SubmitField('This and its children ')
