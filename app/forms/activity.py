from flask_babel import lazy_gettext as _  # gettext
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SelectField, TextAreaField, DateTimeField
from wtforms.validators import InputRequired

from app.forms.fields import CustomFormSelectField, EmailField
from app.forms.util import FieldVerticalSplit


class CreateForm(FlaskForm):
    form_id = CustomFormSelectField(_('Form'))
    nl_name = StringField(_('Dutch name'),
                          validators=[InputRequired()])
    nl_description = TextAreaField(_('Dutch description'),
                                   validators=[InputRequired()])
    en_name = StringField(_('English name'),
                          validators=[InputRequired()])
    en_description = TextAreaField(_('English description'),
                                   validators=[InputRequired()])

    names = FieldVerticalSplit([['nl_name', 'nl_description'],
                                ['en_name', 'en_description']])

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
        if self.start_time.data >= self.end_time.data:
            self.start_time.errors.append(
                _("Start time must be before end time"))
            # Append empty string to mark the field red.
            self.end_time.errors.append('')
            return False

        return True


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
