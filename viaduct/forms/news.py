from flask_wtf import Form
from wtforms import TextField, TextAreaField, DateField
from wtforms.validators import InputRequired, Optional
from flask.ext.babel import _

from datetime import date, timedelta


class NewsForm(Form):
    title = TextField(
        _('Title'), validators=[
            InputRequired(_('Title') + ' ' + _('is required'))])
    content = TextAreaField(
        _('Content'), validators=[
            InputRequired(_('Content') + ' ' + _('is required'))])
    publish_date = DateField(
        _('Publish date'), default=str(date.today()), validators=[
            InputRequired(_('Publish date') + ' ' + _('is required'))])
    archive_date = DateField(
        _('Archive date'), default=str(date.today() + timedelta(days=31)),
        validators=[Optional()])

    def validate(self):
        archive_date = self.archive_date.data
        publish_date = self.publish_date.data
        result = True

        if not Form.validate(self):
            result = False
        if archive_date and publish_date > archive_date:
            self.archive_date.errors.append(
                _('Archive date needs to be after the publish date.'))
            result = False
        return result
