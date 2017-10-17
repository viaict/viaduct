from sqlalchemy.orm import raiseload

from app import db
from app.models.request_ticket import PasswordTicket


def save(ticket):
    db.session.add(ticket)
    db.session.commit()


def create_password_ticket():
    return PasswordTicket()


def find_password_ticket_by_hash(hash_):
    return db.session.query(PasswordTicket) \
        .filter_by(hash == hash_).options(raiseload('*')).one_or_none()
