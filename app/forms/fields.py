from flask_babel import lazy_gettext as _  # noqa
from wtforms import DecimalField as WtfDecimalFields
from wtforms import IntegerField, SelectField, StringField
from wtforms.validators import Email, ValidationError, URL

from app.models.course import Course
from app.models.education import Education
from app.models.group import Group


class CustomFormSelectField(IntegerField):
    pass


class CourseSelectField(SelectField):
    def __init__(self, label='', validators=None, **kwargs):
        super(CourseSelectField, self).__init__(label, validators, **kwargs)
        self.coerce = int
        courses = Course.query.order_by(Course.name).all()
        self.choices = [(c.id, c.name) for c in courses]


class EducationSelectField(SelectField):
    def __init__(self, label='', validators=None, **kwargs):
        super(EducationSelectField, self).__init__(label, validators, **kwargs)
        self.coerce = int
        educations = Education.query.order_by(Education.name).all()
        self.choices = [(e.id, e.name) for e in educations]


class GroupSelectField(SelectField):
    def __init__(self, label='', validators=None, **kwargs):
        super(GroupSelectField, self).__init__(label, validators, **kwargs)
        self.coerce = int
        groups = Group.query.order_by(Group.name).all()
        self.choices = [(g.id, g.name) for g in groups]


class DecimalField(WtfDecimalFields):

    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", ".")
        return super(DecimalField, self).process_formdata(valuelist)


class EmailListField(StringField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._email_validator = Email()

    def pre_validate(self, form):
        origdata = self.data
        self.data += "@svia.nl"
        try:
            self._email_validator(form, self)
            # The current version of WTForms does not check for spaces
            # and multiple '@' characters.
            # this is fixed but not released yet, so we do it ourselves
            if " " in self.data or "@" in origdata:
                raise ValidationError()
        except ValidationError:
            raise ValidationError(_('Invalid email list name.'))
        finally:
            self.data = origdata

    def process_formdata(self, valuelist):
        super().process_formdata([d.strip().lower() for d in valuelist])


class EmailField(StringField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._email_validator = Email()

    def pre_validate(self, form):
        self._email_validator(form, self)
        # The current version of WTForms does not check for spaces
        # this is fixed but not released yet, so we do it ourselves
        if " " in self.data:
            raise ValidationError(self.gettext('Invalid email address.'))

        super().pre_validate(form)

    def process_formdata(self, valuelist):
        super().process_formdata([d.strip().lower() for d in valuelist])


class URLList(URL):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, form, field):
        original_field_data = field.data

        try:
            for uri in [uri.strip() for uri in field.data.split(",")]:
                field.data = uri
                message = self.message
                if message is None:
                    message = field.gettext('Invalid URL.')

                match = super(URL, self).__call__(form, field, message)
                if not self.validate_hostname(match.group('host')):
                    raise ValidationError(message)
        finally:
            field.data = original_field_data
