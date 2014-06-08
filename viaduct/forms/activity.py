from flask_wtf import Form
from flask_wtf.file import FileField
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Email


class CreateForm(Form):
    name = StringField(u'Naam', validators=[InputRequired()])
    description = TextAreaField(u'Beschrijving', validators=[InputRequired()])
    start_date = StringField(u'start_time', validators=[InputRequired()])
    start_time = StringField(u'start_time', validators=[InputRequired()])
    end_date = StringField(u'Venue')
    end_time = StringField(u'Venue')
    location = StringField(u'Locatie',
                           default="Studievereniging VIA, Science Park 904,\
                           1098 Amsterdam Nederland")
    privacy = StringField(u'Privacy')
    price = StringField(u'Prijs')
    picture = FileField(u'Plaatje')
    venue = StringField(u'Venue')
    form_id = SelectField('Formulier', coerce=int)


class ActivityForm(Form):
    email = StringField(u'E-mail address', validators=[InputRequired(),
                                                       Email()])
    first_name = StringField(u'First name', validators=[InputRequired()])
    last_name = StringField(u'Last name', validators=[InputRequired()])
    student_id = StringField(u'Student ID', validators=[InputRequired()])
    education_id = SelectField(u'Education', coerce=int)
