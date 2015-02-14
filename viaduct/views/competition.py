from flask import Blueprint, render_template

blueprint = Blueprint('competition', __name__, url_prefix='/competition')


@blueprint.route('/', methods=['GET', 'POST'])
def overview():
    return render_template('competition/overview.htm')


@blueprint.route('/teams/create', methods=['GET', 'POST'])
@blueprint.route('/teams/edit/<int:team_id>', methods=['GET', 'POST'])
def edit_team(team_id=None):
    if team_id:
        # doe iets
    else:
        # doe iets anders

    if form.validate_on_submit():

    return render_template('competition/add_team.htm')
