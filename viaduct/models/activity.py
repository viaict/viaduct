from viaduct import db
from viaduct import get_locale
from datetime import datetime, timedelta
from viaduct.models import BaseEntity
from babel.dates import format_timedelta, format_datetime
from sqlalchemy import event
from flask.ext.babel import lazy_gettext as _  # gettext


# Model to support Facebook/Google API integration
class Activity(db.Model, BaseEntity):
    __tablename__ = 'activity'

    prints = ('id', 'name', 'start_time', 'end_time')

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    en_name = db.Column(db.String(256))
    en_description = db.Column(db.String(2048))
    nl_name = db.Column(db.String(256))
    nl_description = db.Column(db.String(2048))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    location = db.Column(db.String(64))
    privacy = db.Column(db.String(64))
    price = db.Column(db.String(16))
    picture = db.Column(db.String(255))
    venue = db.Column(db.Integer)  # venue ID
    updated_time = db.Column(db.DateTime, default=datetime.now())
    form_id = db.Column(db.Integer, db.ForeignKey('custom_form.id'))

    google_event_id = db.Column(db.String(64))
    owner = db.relationship('User',
                            backref=db.backref('activities', lazy='dynamic'))

    def __init__(self, owner_id=None, en_name="", en_description="",
                 nl_name="", nl_description="", start_time=None,
                 end_time=None,
                 location="Studievereniging VIA, Science Park 904, "
                 "1098 XH Amsterdam", privacy=_("Public"),
                 price=_("Free"), picture=None, venue=1, form_id=None):

        if not start_time:
            today = datetime.now()
            start_time = datetime(today.year, today.month, today.day, 17)
            end_time = start_time + timedelta(hours=5)

        self.owner_id = owner_id

        # Name and description is set to None during initialisation of the
        # object, when the data is loading through SQLAlchemy, the name and
        # description are set. For more info see set_activity_locale().
        self.name = None
        self.nl_name = nl_name
        self.en_name = en_name

        self.description = None
        self.nl_description = nl_description
        self.en_description = en_description

        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.privacy = privacy
        self.price = price
        self.picture = picture
        self.venue = 1
        self.form_id = form_id

    def get_time(self):
        """
        Get a proper representation of all datetime date, based on the time the
        event is gonna take/when it is going to start/when it's gonna end
        """
        today = datetime.now()
        if self.start_time.month == self.end_time.month and \
                self.start_time.day == self.end_time.day:
            if self.start_time.year == today.year:
                return format_datetime(self.start_time, 'EEEE d MMM, H:mm - ',
                                       locale=get_locale()).capitalize() + \
                    format_datetime(self.end_time, 'H:mm', locale=get_locale())
            else:
                return format_datetime(self.start_time,
                                       'EEEE d MMM YYYY, H:mm - ',
                                       locale=get_locale()).capitalize() + \
                    format_datetime(self.end_time, 'H:mm', locale=get_locale())
        else:
            if self.start_time.year == today.year:
                return format_datetime(self.start_time, 'EEE d MMM (H:mm) - ',
                                       locale=get_locale()).capitalize() + \
                    format_datetime(self.end_time, 'EEE d MMM (H:mm)',
                                    locale=get_locale()).capitalize()
            else:
                return self.start_time.strftime("%a. %d %b %Y (%H:%M) - ") + \
                    self.end_time.strftime("%a. %d %b %Y (%H:%M)")

    def is_in_future(self):
        return datetime.now() < self.start_time

    def is_in_past(self):
        return datetime.now() >= self.end_time

    def get_short_description(self, characters):
        """
        Get a description cut a number of characters, with suffixed dots.
        """
        if (len(self.description) > characters):
            short_description = self.description[:characters].strip()
            words = short_description.split(' ')[:-1]

            return ' '.join(words) + '...'

        return self.description

    def get_timedelta_to_start(self):
        """
        Returns locale based description of time left to start.
        """
        return format_timedelta(datetime.now() - self.start_time,
                                locale=get_locale())

    def get_timedelta_from_end(self):
        """
        Returns locale based description of time in the past.
        """
        return format_timedelta(datetime.now() - self.end_time,
                                locale=get_locale())

    def get_timedelta_to_end(self):
        """
        Returns locale based description of time until the end of the activity.
        """
        return format_timedelta(self.end_time - datetime.now(),
                                locale=get_locale())

    def format_form_time(self, time):
        return time.strftime("%Y-%m-%d %H:%M")

    def till_now(self):
        """
        Returns a locale based description of datetimedelta till now
        """
        if self.is_in_future():
            return _('in') + ' %s' % (self.get_timedelta_to_start())

        if self.is_in_past():
            return '%s ' % (self.get_timedelta_from_end()) + _('ago')

        return _('still') + ' %s' % (self.get_timedelta_to_end())


@event.listens_for(Activity, 'load')
def set_activity_locale(activity, context):
    """
    This function is called after an Activity model is filled with data from
    the database, but before is used in all other code.

    Use the locale of the current user/client to determine which language to
    display on the whole website. If the users locale is unavailable, select
    the alternative language, suffixing the title of the activity with the
    displayed language.
    """
    locale = get_locale()
    nl_available = activity.nl_name and activity.nl_description
    en_available = activity.en_name and activity.en_description
    if locale == 'nl' and nl_available:
        activity.name = activity.nl_name
        activity.description = activity.nl_description
    elif locale == 'en' and en_available:
        activity.name = activity.en_name
        activity.description = activity.en_description
    elif nl_available:
        activity.name = activity.nl_name + " (" + _('Dutch') + ")"
        activity.description = activity.nl_description
    elif en_available:
        activity.name = activity.en_name + " (" + _('English') + ")"
        activity.description = activity.en_description
    else:
        activity.name = 'N/A'
        activity.description = 'N/A'
