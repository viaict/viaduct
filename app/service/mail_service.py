from app.utils import google


def send_mail(to, subject, email_template, **kwargs):
    google.send_mail(to, subject, email_template, **kwargs)
