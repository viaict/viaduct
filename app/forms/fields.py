from flask_babel import lazy_gettext as _  # noqa
from wtforms import DecimalField as WtfDecimalFields
from wtforms import IntegerField, SelectField, \
    SelectMultipleField, StringField
from wtforms.validators import Email, ValidationError, URL
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField

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


class OrderedSelectMultipleField(SelectMultipleField):
    _choices_labels = None

    def iter_choices(self):
        if not self._choices_labels:
            self._choices_labels = {
                self.coerce(value): label for value, label in self.choices
            }

        if self.choices:
            selected = set(self.data) if self.data else set()
            unselected = set(value for value, _ in self.choices
                             if value not in selected)

            for value in self.data:
                yield (value, self._choices_labels[value], True)

            for value in unselected:
                yield (value, self._choices_labels[value], False)


class OrderedQuerySelectMultipleField(QuerySelectMultipleField):
    def _get_data(self):
        formdata = self._formdata
        if formdata is not None:
            data = []
            object_dict = {
                pk: obj for pk, obj in self._get_object_list()
            }

            for pk in formdata:
                if pk in object_dict:
                    data.append(object_dict[pk])
                else:
                    self._invalid_formdata = True

            if formdata:
                self._invalid_formdata = True
            self._set_data(data)

        return self._data

    data = property(_get_data, QuerySelectMultipleField._set_data)

    def process_formdata(self, valuelist):
        self._formdata = valuelist

    def iter_choices(self):
        objects = self._get_object_list()
        object_to_pk = {
            obj: pk for pk, obj in objects
        }

        all_objects = set(obj for _, obj in objects)
        selected_objects = set(self.data)

        for obj in self.data:
            if obj in object_to_pk:
                yield (object_to_pk[obj], self.get_label(obj), True)

        for obj in all_objects - selected_objects:
            if obj in object_to_pk:
                yield (object_to_pk[obj], self.get_label(obj), False)


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
