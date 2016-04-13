from flask import flash


def flash_form_errors(form):
    for field, errors in list(form.errors.items()):
        for error in errors:
            flash('%s' % error, 'danger')
