from viaduct import db
from datetime import datetime

from viaduct.models import BaseEntity
from viaduct.models.user import User

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class Challenge(db.Model, BaseEntity):
    __tablename__ = 'challenge'

    name = db.Column(db.String(200), unique=True)
    description = db.Column(db.Text())
    hint = db.Column(db.String(1024))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    parent_id = db.Column(db.Integer, db.ForeignKey('challenge.id'))
    weight = db.Column(db.Integer)
    answer = db.Column(db.Text())
    type = db.Column(db.Enum('Text', 'Image', 'Custom'))

    def __init__(self, name='', description='', hint=None,
                 start_date=None, end_date=None, parent_id=None, 
                 weight=None, type='Text', answer=None):
        self.name = name
        self.description = description
        self.hint = hint
        self.start_date = start_date
        self.end_date = end_date
        self.parent_id = parent_id
        self.weight = weight
        self.answer = answer
        self.type = type

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id' : self.id,
           'name': self.name,
           'hint': self.hint,
           'description': self.description,
           'start_date': dump_datetime(self.start_date),
           # This is an example how to deal with Many2Many relations
           'end_date'  : dump_datetime(self.end_date),
           'parent_id'  : self.parent_id,
           'answer'  : self.answer,
           'type'  : self.type,
       }

class Submission(db.Model, BaseEntity):
    __tablename__ = 'submission'

    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'))
    challenge_rev = db.relationship(Challenge, backref=db.backref('submission',
                               lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User,
                           backref=db.backref('submission', lazy='dynamic'))
    answer = db.Column(db.Text())
    image_path = db.Column(db.String(256))
    approved = db.Column(db.Boolean)

    def __init__(self, challenge_id=None,
                 challenge=None, user_id=None, user=None,
                 submission=None, image_path=None, approved=False):
        self.challenge_id = challenge_id
        self.challenge = challenge
        self.user_id = user_id
        self.user = user
        self.submission = submission
        self.image_path = image_path
        self.approved = approved
