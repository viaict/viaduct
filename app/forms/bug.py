from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired
from werkzeug.datastructures import MultiDict


class CreateIssueForm(FlaskForm):
    summary = StringField(
        _('Title'),
        validators=[
            InputRequired(message=_('No title entered'))]
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
