from flask_babel import lazy_gettext as _  # gettext
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SelectField, TextAreaField, DateTimeField
from wtforms.validators import InputRequired

from app.forms.fields import CustomFormSelectField, EmailField
from app.forms.util import FieldTabGroup, FieldTab, FieldVerticalSplit


class CreateForm(FlaskForm):
    form_id = CustomFormSelectField(_('Form'))
    nl_name = StringField(_('Dutch name'))
    nl_description = TextAreaField(_('Dutch description'))
    en_name = StringField(_('English name'))
    en_description = TextAreaField(_('English description'))

    details = FieldTabGroup([
        FieldTab(_('Dutch details'), ['nl_name', 'nl_description']),
        FieldTab(_('English details'), ['en_name', 'en_description'])
    ])

    start_time = DateTimeField(
        _('Start time'), validators=[
            InputRequired(_('Start time') + " " + _('required'))],
        format='%Y-%m-%d %H:%M')
    end_time = DateTimeField(
        _('End time'), format='%Y-%m-%d %H:%M')

    timerange = FieldVerticalSplit([['start_time'], ['end_time']])

    location = StringField(
        _('Location'), default='Studievereniging VIA, Science Park 904,\
        1098 XH Amsterdam, Nederland')

    price = StringField(_('Displayed price'), default=0)
    picture = FileField(_('Image'))

    # Override validate from the Form class
    def validate(self):

        # Validate all other fields with default validators
        if not FlaskForm.validate(self):
            return False

        # Test if either english or dutch is entered
        result = True
        if not (self.nl_name.data or self.en_name.data):
            self.nl_name.errors.append(
                _('Either Dutch or English name required'))
            result = False
        if not (self.nl_description.data or self.en_description.data):
            self.nl_description.errors.append(
                _('Either Dutch or English description required'))
            result = False

        # XOR the results to test if both of a language was given
        if bool(self.nl_name.data) != bool(self.nl_description.data):
            self.nl_name.errors.append(
                _('Dutch name requires Dutch description and vice versa'))
            result = False
        if bool(self.en_name.data) != bool(self.en_description.data):
            self.en_name.errors.append(
                _('English name requires English description and vice versa'))
            result = False

        return result


class ActivityForm(FlaskForm):
    email = EmailField(
        _('E-mail address'), validators=[InputRequired()])
    first_name = StringField(
        _('First name'), validators=[
            InputRequired(_('First name') + " " + _('required'))])
    last_name = StringField(
        _('Last name'), validators=[
            InputRequired(_('Last name') + " " + _('required'))])
    student_id = StringField(
        _('Student ID'), validators=[
            InputRequired(_('Student ID') + " " + _('required'))])
    education_id = SelectField(
        _('Education'), coerce=int)
    introductions = SelectField(_('Number of extra attendants'), coerce=int)
