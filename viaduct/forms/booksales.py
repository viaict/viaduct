from flask_wtf import Form
from wtforms import FloatField, StringField, IntegerField, SelectField
from wtforms.validators import InputRequired

from viaduct.models.booksales import MultiCheckboxField
from viaduct import application

DATE_FORMAT = application.config['DATE_FORMAT']


class AddBookForm(Form):
    title = StringField('title', validators=[InputRequired()])
    price = FloatField('price', validators=[InputRequired()])
    isbn = StringField('isbn', validators=[InputRequired()])
    stock = IntegerField('stock', validators=[InputRequired()])


class AddSaleForm(Form):
    books = MultiCheckboxField('books', validators=[InputRequired()])
    student_number = IntegerField('student_number',
                                  validators=[InputRequired()])
    payment = SelectField('payment', validators=[InputRequired()],
                          choices=[(1, 'pin'), (2, 'contant')])

    def load_books(self, books):
        self.books.choices = map(lambda x: (x.id, x.title), books)
