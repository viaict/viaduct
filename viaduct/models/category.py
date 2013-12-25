from viaduct import db

category_page = db.Table('category_page',
	db.Column('category_id', db.Integer, db.ForeignKey('category.id')),
	db.Column('page_id', db.Integer, db.ForeignKey('page.id'))
)

# relationship required for adjacency list (self referencial many to many
# relationship)
category_category = db.Table('category_category',
	db.Column('super_id', db.Integer, db.ForeignKey('category.id')),
	db.Column('sub_id', db.Integer, db.ForeignKey('category.id')))

class Category(db.Model):
	""" Categories for pages similar to
	https://www.mediawiki.org/wiki/Help:Categories """

	__tablename__ = 'category'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(256), unique=True)

	pages = db.relationship('Page', secondary=category_page,
		backref=db.backref('categories'))

	sub_categories = db.relationship('Category',
		secondary=category_category,
		primaryjoin=id==category_category.c.super_id,
		secondaryjoin=id==category_category.c.sub_id,
		backref='super_categories')


	def __init__(self, name):
		self.name = name

	def has_parent_category(self):
		#categories = Category.query(filter(func.count(Category.super_categories)>0)).all()
		return len(super_categories) > 0


	def __str__(self):
		return "Category: %s" % self.name
