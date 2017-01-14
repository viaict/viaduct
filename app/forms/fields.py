from wtforms import IntegerField, SelectField
# from wtforms.utils import unset_value


class CustomFormSelectField(IntegerField):
    pass


class CourseSelectField(SelectField):
    pass


class EducationSelectField(SelectField):
    pass


class FieldGroup:
    def __init__(self, groups):
        self.groups = groups
