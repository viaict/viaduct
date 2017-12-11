from wtforms import IntegerField, SelectField, StringField
from wtforms import DecimalField as WtfDecimalFields
from wtforms.validators import Email, ValidationError
from flask_babel import lazy_gettext as _, gettext  # noqa
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
