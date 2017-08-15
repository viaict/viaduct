from flask_babel import lazy_gettext as _  # gettext
from flask_wtf import Form
from wtforms import BooleanField, DateField, DateTimeField, DecimalField, FileField, FormField, IntegerField, PasswordField, RadioField, SelectField, StringField, SubmitField, TextAreaField, TextField
from app.forms.fields import CustomFormSelectField, CourseSelectField, EducationSelectField
from app.forms.util import FieldTabGroup, FieldTab, FieldVerticalSplit
from flask_wtf.recaptcha import RecaptchaField
from wtforms.validators import InputRequired, Length, StopValidation


class TestForm(Form):
    f1 = BooleanField('Field 1 Boolean', default=True)
    f2 = CustomFormSelectField('Field 2 CustomFormSelect')
    f3 = DateField('Field 3 Date')
    f4 = DateTimeField('Field 4 DateTime')
    f5 = DecimalField('Field 5 Decimal', validators=[InputRequired()])
    f6 = FileField('Field 6 File', validators=[InputRequired()])
    f8 = IntegerField('Field 8 Integer', validators=[InputRequired()])
    f9 = PasswordField('Field 9 Password', validators=[InputRequired()])
    f10 = RadioField('Field 10 Radio', choices=[
        ('c1', 'Choice 1'),
        ('c2', 'Choice 2'),
        ('c3', 'Choice 3')], validators=[InputRequired()])
    f11 = RecaptchaField('Field 11 Recaptcha')
    f12 = SelectField('Field 12 Select', choices=[
        ('c1', 'Choice 1'),
        ('c2', 'Choice 2'),
        ('c3', 'Choice 3')])
    f13 = StringField('Field 13 String', validators=[InputRequired(), Length(min=5)])
    # f14 = SubmitField('Field 14 Submit')
    f15 = TextAreaField('Field 15 TextArea', validators=[InputRequired()])
    f16 = TextField('Field 16 Text', validators=[InputRequired()])
    f17 = CourseSelectField('Field 17 CourseSelect', validators=[InputRequired()])
    f18 = EducationSelectField('Field 18 EducationSelectField', validators=[InputRequired()])



# button, submit, checkbox, textarea, datefield, datetimefield_picker, datefield_picker, select, file, education_select, course_select, custom_form_select

    nl_name = StringField(_('Dutch name'))
    nl_description = TextAreaField(_('Dutch description'))
    en_name = StringField(_('English name'))
    en_description = TextAreaField(_('English description'))

    groups = FieldTabGroup([
        FieldTab(_('Dutch details'), ['f3', 'f4']),
        FieldTab(_('English details'), ['f5', 'f6']),
    ])
    split_test = FieldVerticalSplit(
        [['f8'], ['f9'], ['f10']]
    )


    # date_begin = DateField('Start')
    # date_end = DateField('End')
    # date = FieldVerticalSplit([
        # ['date_begin'],
        # ['date_end'],
    # ])

    # group = SelectField('Group',
                        # choices=[
                            # ('c1', 'Choice 1'),
                            # ('c2', 'Choice 2'),
                            # ('c3', 'Choice 3')]
                        # )
    # coordinator = SelectField('Coordinator',
                              # choices=[
        # ('c1', 'Choice 1'),
        # ('c2', 'Choice 2'),
        # ('c3', 'Choice 3')]
                              # )
    # is_interim = BooleanField('Interim')

    # split_test = FieldVerticalSplit(
        # [['group'], ['coordinator'], ['is_interim']]
    # )
