from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired

from app.forms.fields import URLList


class OAuthClientForm(FlaskForm):
    name = StringField(
        _('Name'), description=_("Display name of the client"),
        validators=[InputRequired()])
    description = StringField(
        _('Description'),
        description=_("Description of the client, usage for example"),
        validators=[InputRequired()])
    redirect_uri = StringField(
        _("Authorized callback URLs"),
        description=_("Comma separated, regex allowed"),
        validators=[InputRequired(), URLList(require_tld=False)])
