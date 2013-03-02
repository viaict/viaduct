import datetime
from sqlalchemy import desc

from application import db

class Page(db.Model):
	__tablename__ = 'page'

	id = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.String(256), unique=True)
	revisions = db.relationship('PageRevision', backref='page', lazy='dynamic')

	def __init__(self, path):
		self.path = path

	def get_most_recent(self):
		revision = PageRevision.query.filter(PageRevision.page_id == self.id)
		print revision
		revision = revision.order_by(PageRevision.timestamp.desc()).first()
		print revision
		print PageRevision.query.all()
		revision['path'] = self.path
		return revision


class PageRevision(db.Model):
	__tablename__ = 'page_revision'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(128))
	content = db.Column(db.Text)
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'))

	def __init__(self, page, author, title, content,
		timestamp=datetime.datetime.utcnow()):
		self.title = title
		self.content = content
		self.user_id = author.id
		self.page_id = page.id
		self.timestamp = timestamp

