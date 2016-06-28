from flask_babel import lazy_gettext as _
from flask_wtf import Form
from wtforms import TextField, TextAreaField, DateField
from wtforms.validators import InputRequired, Optional

from datetime import date, timedelta


class NewsForm(Form):
    nl_title = TextField(_('Dutch title'))
    nl_content = TextAreaField(_('Dutch content'))
    en_title = TextField(_('English title'))
    en_content = TextAreaField(_('English content'))

    publish_date = DateField(
        _('Publish date'), default=str(date.today()), validators=[
            InputRequired(_('Publish date') + ' ' + _('is required'))])
    archive_date = DateField(
        _('Archive date'), default=str(date.today() + timedelta(days=31)),
        validators=[Optional()])

    def validate(self):

        # Validate all other fields with default validators
        if not Form.validate(self):
            return False
        result = True

        archive_date = self.archive_date.data
        publish_date = self.publish_date.data
        if archive_date and publish_date > archive_date:
            self.archive_date.errors.append(
                _('Archive date needs to be after the publish date.'))
            result = False

        # Test if either english or dutch is entered
        result = True
        if not (self.nl_title.data or self.en_title.data):
            self.nl_title.errors.append(
                _('Either Dutch or English title required'))
            result = False
        if not (self.nl_content.data or self.en_content.data):
            self.nl_content.errors.append(
                _('Either Dutch or English content required'))
            result = False

        # XOR the results to test if both of a language was given
        if bool(self.nl_title.data) != bool(self.nl_content.data):
            self.nl_title.errors.append(
                _('Dutch title requires Dutch content and vice versa'))
            result = False
        if bool(self.en_title.data) != bool(self.en_content.data):
            self.en_title.errors.append(
                _('English title requires English content and vice versa'))
            result = False

        return result
