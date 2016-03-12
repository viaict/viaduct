from flask import abort
from app.models.booksales import Book, Sale
from app import db
from app.api.module import ModuleAPI


class BookSalesAPI:
    @staticmethod
    def commit_sale_to_db(books, student_number, payment):
        if not ModuleAPI.can_write('booksales'):
            abort(403)

        price = 0
        sale = Sale(student_number, payment)
        db.session.add(sale)
        db.session.commit()
        for book_id in books:
            book = Book.query.get(book_id)
            sale.books.append(book)
            price += book.price
            book.update_stock(-1)
            db.session.add(book)

        sale.price = price
        db.session.commit()

    @staticmethod
    def commit_book_to_db(book_id, title, price, isbn, stock):
        """
        Adds a new book to the database

        Returns succes(boolean), message (string). Message is the book.id if
        succes is true, otherwise it contains what exactly went wrong.

        In case of succes the book is entered into the database
        """

        if not ModuleAPI.can_write('booksales'):
            abort(403)

        if book_id == -1:
            book = Book(title, price, isbn, stock)
            db.session.add(book)
            db.session.commit()
            return True, book.id

        book = Book.query.filter(Book.id == book_id).first()
        book.title = title
        book.price = price
        book.isbn = isbn
        book.stock = stock
        db.session.add(book)
        db.session.commit()

        return True, book.id

    def edit_book(book_id, title, price, isbn, stock):
        if not ModuleAPI.can_write('booksales'):
            abort(403)

        book = Book.query.filter(Book.id == book_id).first()
        book.title = title
        book.price = price
        book.isbn = isbn
        book.stock = stock
        db.session.add(book)
        db.session.commit()

        return True, book.id
