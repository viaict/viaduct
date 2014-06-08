from flask_wtf import Form
from wtforms import FieldList, FormField, SubmitField, \
    BooleanField, HiddenField, SelectField

from wtforms import Form as UnsafeForm


class SurveyFieldForm(UnsafeForm):
    keep_alive = HiddenField('KeepAlive', default='keep-alive')
    field_type = SelectField('Field Type',
                             choices=[('text', 'Text field'),
                                      ('select', 'Select field'),
                                      ('boolean', 'Boolean field')
                                      ])
    view = BooleanField('View')


class CreateSurveyForm(Form):
    fields = FieldList(FormField(SurveyFieldForm))
    add_field = SubmitField('Add Field')
    create_survey = SubmitField('Create Survey')
