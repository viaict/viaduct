from viaduct import db
from viaduct.models import BaseEntity
# from viaduct.models.course import Course
# from viaduct.models.education import Education
# from viaduct.models.user import User
# import datetime


class Sponsor(db.Model, BaseEntity):
    """
    Model used to store sponsor data
    """
    __tablename__ = 'sponsor'

    name = db.Column(db.String(128))
