import random
import string
from datetime import datetime

from app.exceptions.base import ResourceNotFoundException
from app.repository import password_reset_repository
from app.service import user_service, mail_service


def build_hash(n):
    available_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(available_characters) for _ in range(n))


def get_valid_ticket(hash_):
    ticket = password_reset_repository.find_password_ticket_by_hash(hash_)
    if ticket is None or (datetime.now() - ticket.created).seconds > 3600:
        raise ResourceNotFoundException("password reset ticket", hash_)
    return ticket


def reset_password(ticket, new_password):
    return user_service.set_password(ticket.user_id, new_password)


def create_password_ticket(email):
    user = user_service.get_user_by_email(email)

    hash_ = build_hash(20)

    ticket = password_reset_repository.create_password_ticket()
    ticket.user_id = user.id
    ticket.hash = hash_

    password_reset_repository.save(ticket)

    mail_service.send_mail(
        to=user.email,
        subject='Password reset https://svia.nl',
        email_template='email/forgot_password.html',
        user_name=user.name,
        hash_=hash_)
