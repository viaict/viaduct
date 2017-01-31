from wtforms import IntegerField, SelectField
from app.models import Course, Education


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
