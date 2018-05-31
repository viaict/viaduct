# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import abort, flash, render_template, request
from flask_babel import lazy_gettext as _
from flask_login import current_user

from app.forms.bug import CreateIssueForm
from app.service import gitlab_service
from app.views import redirect_back

blueprint = Blueprint('bug', __name__, url_prefix='/bug')


@blueprint.route('/report/', methods=['GET', 'POST'])
def report():
    if current_user.is_anonymous or not current_user.has_paid:
        abort(403)

    form = CreateIssueForm(request.form)

    if form.validate_on_submit():
        response = gitlab_service.create_gitlab_issue(
            form.summary.data, current_user.email, form.description.data)
        if response:
            flash('The bug has been reported!', 'success')
            return redirect_back()
        else:
            flash(_('Something went wrong.'), 'danger'), 500

    return render_template('bug/report.htm', form=form)
