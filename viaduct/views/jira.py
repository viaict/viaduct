# -*- coding: utf-8 -*-
from flask import abort, flash, render_template, request, redirect, url_for
from flask import Blueprint

from flask.ext.login import current_user

from viaduct.helpers import flash_form_errors
from viaduct.forms.jira import CreateIssueForm
from viaduct.api.jira import JiraAPI

blueprint = Blueprint('jira', __name__)


@blueprint.route('/create-issue/', methods=['GET', 'POST'])
def create_issue():

    if not current_user:
        abort(403)

    form = CreateIssueForm(request.form)

    if form.validate_on_submit():

        # Use JiraAPI to do a POST request to https://viaduct.atlassian.net
        response = JiraAPI.create_issue(form)

        if response:
            flash('Issue is geupload!', 'success')
            return redirect(url_for('home.home'))
        else:
            flash('Er is iets mis gegaan', 'danger')

    else:
        flash_form_errors(form)

    return render_template('jira/create_issue.htm', form=form)
