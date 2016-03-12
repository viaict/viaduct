# -*- coding: utf-8 -*-
from flask import abort, flash, render_template, request, redirect, url_for
from flask import Blueprint

from flask.ext.login import current_user

from viaduct.helpers import flash_form_errors
from viaduct.forms.jira import CreateIssueForm
from viaduct.api.jira import JiraAPI

from flask.ext.babel import lazy_gettext as _

blueprint = Blueprint('jira', __name__)


@blueprint.route('/create-issue/', methods=['GET', 'POST'])
def create_issue():

    if not current_user or not current_user.has_payed:
        abort(403)

    form = CreateIssueForm(request.form)

    if form.validate_on_submit():

        # Use JiraAPI to do a POST request to https://viaduct.atlassian.net
        response = JiraAPI.create_issue(form)

        if response:
            flash(_('The bug has been reported!'), 'success')
            redir = request.args['redir']
            if redir:
                return redirect(redir)
            else:
                return redirect(url_for('home'))
        else:
            flash(_('Something went wrong.'), 'danger')

    else:
        flash_form_errors(form)

    return render_template('jira/create_issue.htm', form=form)
