from flask_wtf import Form
from flask_wtf.file import FileField
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Email


class CreateForm(Form):
    name = StringField('Naam', validators=[InputRequired()])
    description = TextAreaField('Beschrijving', validators=[InputRequired()])
    start_date = StringField('start_time', validators=[InputRequired()])
    start_time = StringField('start_time', validators=[InputRequired()])
    end_date = StringField('Venue')
    end_time = StringField('Venue')
    location = StringField('Locatie',
                           default="Studievereniging VIA, Science Park 904,\
                           1098 Amsterdam Nederland")
    privacy = StringField('Privacy')
    price = StringField('Prijs')
    picture = FileField('Plaatje')
    venue = StringField('Venue')
    form_id = SelectField('Formulier', coerce=int)


class ActivityForm(Form):
    email = StringField('E-mail address', validators=[InputRequired(),
                                                       Email()])
    first_name = StringField('First name', validators=[InputRequired()])
    last_name = StringField('Last name', validators=[InputRequired()])
    student_id = StringField('Student ID', validators=[InputRequired()])
    education_id = SelectField('Education', coerce=int)
