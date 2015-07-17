from datetime import date
from viaduct import db
from viaduct.models import BaseEntity


class News(db.Model, BaseEntity):
    __tablename__ = 'news'

    title = db.Column(db.Text)
    content = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('news', lazy='dynamic'))

    publish_date = db.Column(db.Date)
    archive_date = db.Column(db.Date)

    def __init__(self, title='', content='', user_id=None,
                 archive_date=None, publish_date=date.today()):

        self.title = title
        self.content = content
        self.user_id = user_id
        self.archive_date = archive_date
        self.publish_date = publish_date

    def get_short_content(self, characters):
        """ Get a shortened version of the total post """
        if len(self.content) > characters:
            short_content = self.content[:characters].strip()

            # Remove the last word
            words = short_content.split(' ')[:-1]

            return ' '.join(words) + '...'

        return self.content
