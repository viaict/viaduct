from flask import Blueprint, request, render_template, abort
from flask_login import current_user

from app.forms import CreateSurveyForm
from app.utils.module import ModuleAPI

blueprint = Blueprint('survey', __name__)


@blueprint.route('/survey/')
def view():
    return 'Hello!'


@blueprint.route('/survey/create/', methods=['GET', 'POST'])
def create():
    if not ModuleAPI.can_write('survey') or current_user.is_anonymous:
        return abort(403)

    form = CreateSurveyForm(request.form)

    if form.validate_on_submit():
        if form.add_field.data:
            form.fields.append_entry()
        elif form.create_survey.data:
            pass

    return render_template('survey/create.htm', form=form)
