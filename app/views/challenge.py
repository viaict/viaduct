import datetime

from flask import Blueprint, render_template, request, \
    jsonify
from flask_login import login_required, current_user

from app.decorators import require_role
from app.forms.challenge import ChallengeForm
from app.models.challenge import Challenge
from app.roles import Roles
from app.service import role_service
from app.utils.challenge import ChallengeAPI

blueprint = Blueprint('challenge', __name__, url_prefix='/challenge')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/dashboard/', methods=['GET', 'POST'])
@require_role(Roles.CHALLENGE_READ)
def view_list(page=1):
    challenge = Challenge()
    form = ChallengeForm(request.form, challenge)

    challenges = ChallengeAPI.fetch_all_challenges_user(current_user.id)
    approved_challenges = \
        ChallengeAPI.fetch_all_approved_challenges_user(current_user.id)
    user_points = ChallengeAPI.get_points(current_user.id)
    ranking = ChallengeAPI.get_ranking()

    challenge_description = ChallengeAPI.get_challenge_description()

    can_write = role_service.user_has_role(Roles.CHALLENGE_WRITE)

    return render_template('challenge/dashboard.htm', challenges=challenges,
                           user_points=user_points, ranking=ranking,
                           approved_challenges=approved_challenges, form=form,
                           challenge_description=challenge_description,
                           can_write=can_write)


# API's
@blueprint.route('/api/fetch_all_challenges', methods=['GET', 'POST'])
@require_role(Roles.CHALLENGE_WRITE)
def fetch_all():
    challenges = ChallengeAPI.fetch_all_challenges()

    return jsonify(challenges=[challenge.serialize for challenge in
                               challenges])


@blueprint.route('/api/get_ranking', methods=['GET', 'POST'])
def get_ranking():
    ranking = ChallengeAPI.get_ranking()

    return jsonify(ranking=[user.serialize for user in ranking])


@blueprint.route('/api/fetch_challenge', methods=['GET', 'POST'])
@blueprint.route('/api/fetch_challenge/', methods=['GET', 'POST'])
@require_role(Roles.CHALLENGE_WRITE)
def fetch_question():
    # Gather all arguments
    if request.args.get('challenge_id'):
        challenge_id = request.args.get('challenge_id')
    else:
        return "Error, no 'challenge_id' given"

    challenge = ChallengeAPI.fetch_challenge(challenge_id)

    return jsonify(challenges=challenge.serialize)


@blueprint.route('/api/create_challenge', methods=['GET', 'POST'])
@require_role(Roles.CHALLENGE_WRITE)
def create_challenge(challenge_id=None):
    # Gather all arguments
    if request.args.get('parent_id'):
        parent_id = request.args.get('parent_id')
    else:
        return "Error, no 'parent_id' given"

    if request.args.get('name'):
        name = request.args.get('name')
    else:
        return "Error, no 'name' given"

    if request.args.get('description'):
        description = request.args.get('description')
    else:
        return "Error, no 'description' given"

    if request.args.get('type'):
        type = request.args.get('type')
    else:
        return "Error, no 'type' given"

    if request.args.get('start_date'):
        start_date = datetime.datetime.strptime(request.args.get('start_date'),
                                                '%Y-%m-%d').date()
    else:
        return "Error, no 'start_date' given"

    if request.args.get('end_date'):
        end_date = datetime.datetime.strptime(request.args.get('end_date'),
                                              '%Y-%m-%d').date()
    else:
        return "Error, no 'end_date' given"

    if request.args.get('answer'):
        answer = request.args.get('answer')
    else:
        return "Error, no 'answer' given"

    if request.args.get('weight'):
        weight = request.args.get('weight')
    else:
        return "Error, no 'weight' given"

    if request.args.get('hint'):
        hint = request.args.get('hint')
    else:
        return "Error, no 'hint' given"

    # Check if the name of the challenge is unique
    if ChallengeAPI.challenge_exists(name):
        return "Error, challenge with name '" + name + "' already exists"

    return ChallengeAPI.create_challenge(name, description, hint, start_date,
                                         end_date, parent_id, weight, type,
                                         answer)


@blueprint.route('/api/new_submission', methods=['GET', 'POST'])
@login_required
def new_submission(challenge_id=None):
    if request.args.get('challenge_id'):
        challenge_id = request.args.get('challenge_id')
    else:
        return "Error, no 'challenge_id' given"

    if request.args.get('submission'):
        submission = request.args.get('submission')
    else:
        return "Error, no 'submission' given"

    new_submission = ChallengeAPI.create_submission(challenge_id=challenge_id,
                                                    user_id=current_user.id,
                                                    submission=submission,
                                                    image_path=None)

    if new_submission is False:
        return "Question is already submitted"

    challenge = ChallengeAPI.fetch_challenge(challenge_id)

    return ChallengeAPI.validate_question(new_submission, challenge)


@blueprint.route('/api/get_points', methods=['GET', 'POST'])
def get_points(user_id=None):
    if request.args.get('user_id'):
        user_id = request.args.get('user_id')
    else:
        return "Error, no 'user_id' given"

    points = ChallengeAPI.get_points(user_id)

    return str(points)
