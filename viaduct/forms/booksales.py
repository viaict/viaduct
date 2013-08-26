from flask.ext.wtf import Form, FloatField, TextField, TextAreaField, DecimalField, FileField, DateTimeField, Required, validators, IntegerField, SelectField, BooleanField, SelectMultipleField

import datetime
from viaduct.models.booksales import Book, Sale, MultiCheckboxField
from viaduct import application

DATE_FORMAT = application.config['DATE_FORMAT']


class AddBookForm(Form):
	title = TextField('title', validators=[Required()])
	price = FloatField('price', validators=[Required()])
	isbn = TextField('isbn', validators=[Required()])
	stock = IntegerField('stock', validators=[Required()])

class AddSaleForm(Form):
	books = MultiCheckboxField('books', validators=[Required()])
	student_number = IntegerField('student_number', validators=[Required()])
	payment = SelectField('payment', validators=[Required()], choices=[(1, 'pin'), (2, 'contant')])

	def load_books(self, books):
		self.books.choices = map(lambda x: (x.id, x.title), books)


