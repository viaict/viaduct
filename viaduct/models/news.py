from viaduct import db
from viaduct.models import BaseEntity


class NewsRevision(db.Model, BaseEntity):
    __tablename__ = 'news_revision'

    item_id = db.Column(db.Integer)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(256))
    content = db.Column(db.Text)
    end_time = db.Column(db.Date)

    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))

    author = db.relationship('User', backref=db.backref('news_items',
                                                        lazy='dynamic'))
    page = db.relationship('Page', backref=db.backref('news_revisions',
                                                      lazy='dynamic'))

    def __init__(self, page=None, author_id=None, title='', content='',
                 end_time=None):
        self.page = page

        self.author_id = author_id
        self.title = title
        self.content = content
        self.end_time = end_time

    def get_short_content(self, characters):
        if (len(self.content) > characters):
            short_content = self.content[:characters].strip()
            words = short_content.split(' ')[:-1]

            return ' '.join(words) + '...'

        return self.content
