from viaduct import db
import datetime
from viaduct.models import BaseEntity
from babel.dates import format_timedelta


# Model to support Facebook/Google API integration
class Activity(db.Model, BaseEntity):
    __tablename__ = 'activity'

    prints = ('id', 'name', 'start_time', 'end_time')

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(256))
    description = db.Column(db.String(2048))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    location = db.Column(db.String(64))
    privacy = db.Column(db.String(64))
    price = db.Column(db.String(16))
    picture = db.Column(db.String(255))
    venue = db.Column(db.Integer)  # venue ID
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now())
    form_id = db.Column(db.Integer, db.ForeignKey('custom_form.id'))

    google_event_id = db.Column(db.Integer)
    owner = db.relationship('User', backref=db.backref('activities',
                                                       lazy='dynamic'))

    def __init__(self, owner_id=None, name="", description="", start_time=None,
                 end_time=None, location="Sciencepark, Amsterdam",
                 privacy="public", price="gratis", picture=None, venue=1,
                 form_id=None):
        if not start_time:
            today = datetime.datetime.now()
            start_time = datetime.datetime(today.year, today.month, today.day,
                                           17)
            end_time = start_time + datetime.timedelta(hours=5)

        self.owner_id = owner_id
        self.name = name
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.privacy = privacy
        self.price = price
        self.picture = picture
        self.venue = 1
        self.form_id = form_id

    def get_time(self):
        today = datetime.datetime.now()
        if self.start_time.month == self.end_time.month and \
                self.start_time.day == self.end_time.day:
            if self.start_time.year == today.year:
                return self.start_time.strftime("%A %d %b, %H:%M - ") + \
                    self.end_time.strftime("%H:%M")
            else:
                return self.start_time.strftime("%A %d %b %Y, %H:%M - ") + \
                    self.end_time.strftime("%H:%M")
        else:
            if self.start_time.year == today.year:
                return self.start_time.strftime("%a. %d %b (%H:%M) - ") + \
                    self.end_time.strftime("%a. %d %b (%H:%M)")
            else:
                return self.start_time.strftime("%a. %d %b %Y (%H:%M) - ") + \
                    self.end_time.strftime("%a. %d %b %Y (%H:%M)")

    def is_in_future(self):
        return datetime.datetime.now() < self.start_time

    def is_in_past(self):
        return datetime.datetime.now() >= self.end_time

    def get_short_description(self, characters):
        if (len(self.description) > characters):
            short_description = self.description[:characters].strip()
            words = short_description.split(' ')[:-1]

            return ' '.join(words) + '...'

        return self.description

    def get_timedelta_to_start(self):
        return datetime.datetime.now() - self.start_time

    def get_timedelta_to_start_formatted(self, locale="nl_NL"):
        """
        Returns over 1 dag
        """
        return format_timedelta(self.get_timedelta_to_start(), locale=locale)

    def get_timedelta_from_end(self):
        return datetime.datetime.now() - self.end_time

    def get_timedelta_from_end_formatted(self, locale='nl_NL'):
        return format_timedelta(self.get_timedelta_from_end(), locale=locale)

    def get_timedelta_to_end(self):
        return self.end_time - datetime.datetime.now()

    def get_timedelta_to_end_formatted(self, locale='nl_NL'):
        return format_timedelta(self.get_timedelta_to_end(), locale=locale)

    def format_form_time(self, time):
        return time.strftime("%Y-%m-%d %H:%M")

    def till_now(self):
        if self.is_in_future():
            return 'over %s' % (self.get_timedelta_to_start_formatted())

        if self.is_in_past():
            return '%s geleden' % (self.get_timedelta_from_end_formatted())

        return 'nog %s' % (self.get_timedelta_to_end_formatted())
