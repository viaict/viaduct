from flask_wtf import Form
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import InputRequired
from werkzeug.datastructures import MultiDict


class CreateIssueForm(Form):
    summary = StringField('Titel',
                          validators=[InputRequired(
                              message='Geen titel opgegeven')])
    issue_type = SelectField('Issue type',
                             choices=[
                                 ('1', 'Bug'),
                                 ('2', 'New Feature'),
                                 ('4', 'Improvement')],
                             default=1,
                             validators=[InputRequired(
                                 message='Geen Issue type opgegeven')])
    description = TextAreaField('Beschrijving',
                                validators=[InputRequired(
                                    message='Geen voornaam opgegeven')])

    def reset(self):
        """ Reset the form, while keeping the token valid """
        blankData = MultiDict([('csrf', self.reset_csrf())])
        self.process(blankData)
