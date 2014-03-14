from viaduct import db
from viaduct.models.page import IdRevision


class NewsRevision(IdRevision):
    __tablename__ = 'news_revision'

    content = db.Column(db.Text)
    end_time = db.Column(db.Date)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('news_revisions',
                                                        lazy='dynamic'))

    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    page = db.relationship('Page', backref=db.backref('news_revisions',
                                                      lazy='dynamic'))

    def __init__(self, page=None, title='', comment='', instance_id=None,
                 content='', author_id=None, end_time=None):
        super(NewsRevision, self).__init__(title, comment, instance_id)

        self.page = page

        self.author_id = author_id
        self.content = content
        self.end_time = end_time

    def get_short_content(self, characters):
        if len(self.content) > characters:
            short_content = self.content[:characters].strip()
            words = short_content.split(' ')[:-1]

            return ' '.join(words) + '...'

        return self.content
