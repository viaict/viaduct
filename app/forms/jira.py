from flask_babel import lazy_gettext as _
from flask_wtf import Form
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import InputRequired
from werkzeug.datastructures import MultiDict


class CreateIssueForm(Form):
    summary = StringField(
        _('Title'),
        validators=[
            InputRequired(message=_('No title entered'))]
    )
    issue_type = SelectField(
        _('Bug type'),
        choices=[('1', 'Bug'), ('2', 'New Feature'), ('4', 'Improvement')],
        default=1,
        validators=[InputRequired(message=_('No issue type supplied'))]
    )
    description = TextAreaField(
        _('Description'),
        validators=[InputRequired(message=_('No description supplied'))]
    )
    recaptcha = RecaptchaField()

    def reset(self):
        """Reset the form, while keeping the token valid."""
        blank_data = MultiDict([('csrf', self.reset_csrf())])
        self.process(blank_data)
