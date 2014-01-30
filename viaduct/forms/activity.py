from flask.ext.wtf import Form, TextAreaField, FileField, TextField, \
    SelectField, Required, Email


class CreateForm(Form):
    name = TextField(u'Naam', validators=[Required()])
    description = TextAreaField(u'Beschrijving', validators=[Required()])
    start_date = TextField(u'start_time', validators=[Required()])
    start_time = TextField(u'start_time', validators=[Required()])
    end_date = TextField(u'Venue')
    end_time = TextField(u'Venue')
    location = TextField(u'Locatie',
                         default="Studievereniging VIA, Science Park 904,\
                         1098 Amsterdam Nederland")
    privacy = TextField(u'Privacy')
    price = TextField(u'Prijs')
    picture = FileField(u'Plaatje')
    venue = TextField(u'Venue')
    form_id = SelectField('Formulier', coerce=int)


class ActivityForm(Form):
    email = TextField(u'E-mail address', validators=[Required(), Email()])
    first_name = TextField(u'First name', validators=[Required()])
    last_name = TextField(u'Last name', validators=[Required()])
    student_id = TextField(u'Student ID', validators=[Required()])
    education_id = SelectField(u'Education', coerce=int)
