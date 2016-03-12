from viaduct import db
from wtforms import widgets, SelectMultipleField
from viaduct.models import BaseEntity

books = db.Table(
    'booksales_sale_group',
    db.Column('book_id', db.Integer, db.ForeignKey('booksales_book.id')),
    db.Column('sale_id', db.Integer, db.ForeignKey('booksales_sale.id'))
)


class Book(db.Model, BaseEntity):
    __tablename__ = 'booksales_book'

    title = db.Column(db.Text)
    price = db.Column(db.Float)
    isbn = db.Column(db.Text)
    stock = db.Column(db.Integer)

    def __init__(self, title, price, isbn, stock):
        self.title = title
        self.price = price
        self.isbn = isbn
        self.stock = stock

    def set_stock(self, stock):
        self.stock = stock
        db.session.commit()

    def update_stock(self, stock_deviation):
        if self.stock >= -stock_deviation and self.stock >= 0:
            self.stock = self.stock + stock_deviation
        else:
            return False, "Not enough stock"
        db.session.commit()
        return True, "Stock edited"


class Sale(db.Model, BaseEntity):
    __tablename__ = 'booksales_sale'

    student_number = db.Column(db.Integer)
    price = db.Column(db.Float)
    payment = db.Column(db.Integer)

    books = db.relationship('Book', secondary=books,
                            backref=db.backref('sales', lazy='dynamic'))

    def __init__(self, student_number, payment):
        self.student_number = student_number
        self.payment = payment


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
