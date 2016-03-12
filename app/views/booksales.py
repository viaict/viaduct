from flask import Blueprint, abort, redirect, url_for
from flask import flash, render_template, request

from app.models.booksales import Book, Sale

from app.utils.module import ModuleAPI
from app.utils.booksales import BookSalesAPI

from app.forms.booksales import AddBookForm, AddSaleForm

blueprint = Blueprint('booksales', __name__, url_prefix='/booksales')


@blueprint.route('/')
def view():
    if not ModuleAPI.can_read('booksales'):
        return abort(403)

    return render_template('booksales/view.htm', books=Book.query.all(),
                           title='Booksales')


@blueprint.route('/sales/')
def view_sales():
    if not ModuleAPI.can_read('booksales'):
        return abort(403)

    return render_template('booksales/sales.htm', sales=Sale.query.all(),
                           title='Booksales')


@blueprint.route('/add_sale/', methods=['GET', 'POST'])
def add_sale():
    if not ModuleAPI.can_write('booksales'):
        return abort(403)

    form = AddSaleForm(request.form)

    if request.method == 'POST':
        BookSalesAPI.commit_sale_to_db(form.books.data,
                                       form.student_number.data,
                                       form.payment.data)
        print((Sale.query.all()))

        return redirect(url_for('booksales.view'))

    books = Book.query.all()

    form.load_books(books)
    return render_template('booksales/add_sale.htm', form=form,
                           title='Booksales')


@blueprint.route('/edit_book/', methods=['GET', 'POST'])
@blueprint.route('/edit_book/<book_id>', methods=['GET', 'POST'])
def edit_book(book_id=-1):
    if not ModuleAPI.can_write('booksales'):
        return abort(403)

    book = Book.query.filter(Book.id == book_id).first()
    if book:
        form = AddBookForm(request.form, title=book.title, price=book.price,
                           isbn=book.isbn, stock=book.stock, id=book.id)
    else:
        form = AddBookForm(request.form)

    if request.method == 'POST':
        message = ""
        if form.title.data == "":
            message = "Title is required"
        elif form.price.data == 0:
            message = "Price is required"
        elif form.isbn.data == "":
            message = "ISBN Number is required"
        elif form.stock.data == "":
            message = "Stock is required"

        result = message == ""

        if result:
            result, message = BookSalesAPI.commit_book_to_db(book_id,
                                                             form.title.data,
                                                             form.price.data,
                                                             form.isbn.data,
                                                             form.stock.data)

        if result:
            flash('The Book was added succesfully', 'success')
            return redirect(url_for('booksales.view'))

    return render_template('booksales/edit_book.htm', form=form,
                           title='Booksales')
