from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, URL


class OAuthClientForm(FlaskForm):
    name = StringField(_('Name'), validators=[InputRequired()])
    description = StringField(_('Description'), validators=[InputRequired()])
    redirect_uri = StringField(_("Authorized callback URL"),
                               validators=[InputRequired(),
                                           URL(require_tld=False)])
