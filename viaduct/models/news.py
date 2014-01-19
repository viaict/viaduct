from viaduct import db
import datetime


class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(256))
    content = db.Column(db.Text)
    end_time = db.Column(db.DateTime)
    post_time = db.Column(db.DateTime, default=datetime.datetime.now())
    update_time = db.Column(db.DateTime, default=None)

    author = db.relationship('User', backref=db.backref('news_items',
                                                        lazy='dynamic'))

    def __init__(self, author_id=None, title='', content='', end_time=None):
        self.author_id = author_id
        self.title = title
        self.content = content
        self.end_time = end_time

    def __repr__(self):
        return '<News(%s, "%s")>' % (self.id, self.end_time)

    def get_short_content(self, characters):
        if (len(self.content) > characters):
            short_content = self.content[:characters].strip()
            words = short_content.split(' ')[:-1]

            return ' '.join(words) + '...'

        return self.content
