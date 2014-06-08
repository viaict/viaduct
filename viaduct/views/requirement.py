from flask import Blueprint, flash, redirect, render_template, request, url_for

from viaduct import db

requirement = Blueprint('requirement', __name__)

@requirement.route('/requirements/', methods=['GET', 'POST'])
@requirement.route('/requirements/<int:page>/', methods=['GET', 'POST'])
def view(page=1):

    requirements = requirement.query.paginate(page, 15, False)

    return render_template('requirement/view.htm', requirements=requirements)

@requirement.route('/requirements/create/', methods=['GET', 'POST'])
def create():
    if not current_user or current_user.email != 'administrator@svia.nl':
        return abort(403)

    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()

        valid_form = True

        if valid_form:
            requirement = Requirement(title, description)

            db.session.add(requirement)
            db.session.commit()

            flash('The requirement has been added.', 'success')

            return redirect(url_for('requirement.view'))

    return render_template('requirement/create.htm')
