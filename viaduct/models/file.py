from viaduct import db


class File(db.Model):
    '''
    A file for pages and generic file usage.
    '''
    __tablename__ = 'file'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))

    page = db.relationship('Page', backref=db.backref('files', lazy='dynamic'))

    def __init__(self, name='', page=None):
        '''
        Constructor.
        '''
        self.name = name
        self.page = page
