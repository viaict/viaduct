from flask import request
from flask_wtf.form import SUBMIT_METHODS


def init_form(cls, **kwargs):
    """
    Initialize a pre-populated form.

    Browsers do not post checkboxes which are not selected, resulting in the
    value being set to `False` when we initialize like

        >>> Form(request.form, obj=obj)

    For that reason the initialization has been split for submission and
    initial request of the form. By initializing the form with this function,
    the issue is solved.
    """
    if request.method in SUBMIT_METHODS:
        return cls(request.form)
    else:
        return cls(**kwargs)
