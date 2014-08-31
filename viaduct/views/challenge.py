from flask import Blueprint, flash, redirect, render_template, request, \
        url_for, abort, jsonify

from sqlalchemy import or_, and_

from datetime import datetime

from flask.ext.login import current_user
from viaduct import application, db
from viaduct.models.challenge import Challenge, Submission
from viaduct.helpers import flash_form_errors
from viaduct.forms import ChallengeForm
from viaduct.api.group import GroupPermissionAPI
from viaduct.api.file import FileAPI
from viaduct.api.challenge import ChallengeAPI

from werkzeug import secure_filename

blueprint = Blueprint('challenge', __name__, url_prefix='/challenge')

# UPLOAD_FOLDER = application.config['UPLOAD_DIR']
# FILE_FOLDER = application.config['FILE_DIR']
# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/dashboard/', methods=['GET', 'POST'])
def view_list(page=1):
    if not GroupPermissionAPI.can_read('challenge'):
        return abort(403)

    challenges = ChallengeAPI.fetch_all_challenges()

    return render_template('challenge/dashboard.htm', challenges=challenges)


@blueprint.route('/create', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:challenge_id>/', methods=['GET', 'POST'])
def edit(challenge_id=None):
    '''
    FRONTEND
    Create, view or edit a challenge.
    '''
    print "tjsdflkjsldfjsdlkf"
    if not GroupPermissionAPI.can_read('vacancy'):
        return abort(403)

    # Select vacancy.
    if challenge_id:
        challenge = ChallengeAPI.fetch_challenge(challenge_id)
    else:
        challenge = Challenge()

    form = ChallengeForm(request.form, challenge)

    # Add companies.
    form.parent_id.choices = [(c.id, c.name) for c in Challenge.query.
                               order_by('name')]

    return render_template('challenge/view.htm', challenge=challenge, form=form)


    # new_challenge = Challenge(name, description, hint, start_date, end_date,
    #                     parent_id, weight, type, answer)
    # db.session.add(new_challenge)
    # db.session.commit()


    # return 'done'#render_template()

@blueprint.route('/update/', methods=['POST'])
@blueprint.route('/update/<int:challenge_id>/', methods=['POST'])
def update(challenge_id=None):
    '''
    BACKEND
    Create, view or edit a challenge.
    '''
    print "tessdfsdfsdfsdfsdt"
    if not GroupPermissionAPI.can_write('challenge'):
        return abort(403)

    # Select challenge.
    if challenge_id:
        challenge = ChallengeAPI.fetch_challenge(challenge_id)
    else:
        challenge = Challenge()

    form = ChallengeForm(request.form, challenge)

    # Add companies.
    form.parent_id.choices = [(c.id, c.name) for c in Challenge.query.
                               order_by('name')]

    if form.validate_on_submit():
        challenge.name = form.name.data
        challenge.description = form.description.data
        challenge.hint = form.hint.data
        challenge.type = form.type.data
        challenge.start_date = form.start_date.data
        challenge.end_date = form.end_date.data
        challenge.weight = form.weight.data
        challenge.answer = form.answer.data
        if form.parent_id.date is not None:
            challenge.parent_id = form.parent_id.data
        else: 
            challenge.parent_id = 0


        print vars(challenge)

        db.session.add(challenge)
        db.session.commit()

        if challenge_id:
            flash('Challenge opgeslagen', 'success')
        else:
            challenge_id = challenge.id
            flash('Challenge aangemaakt', 'success')
    else:
        error_handled = False
        if not form.name.data:
            flash('Geen titel opgegeven', 'error')
            error_handled = True
        if not form.description:
            flash('Geen beschrijving opgegeven', 'error')
            error_handled = True
        if not form.start_date:
            flash('Geen begindatum opgegeven', 'error')
            error_handled = True
        if not form.end_date:
            flash('Geen einddatum opgegeven', 'error')
            error_handled = True
        if not form.weight:
            flash('Geen werklast opgegeven', 'error')
            error_handled = True

        if not error_handled:
            flash_form_errors(form)


    # return edit(challenge_id=challenge_id)
    return redirect(url_for('challenge.edit', challenge_id=challenge_id))


@blueprint.route('/view', methods=['GET', 'POST'])
@blueprint.route('/view/<int:challenge_id>/', methods=['GET', 'POST'])
def view(challenge_id=1):

    challenges = Challenge.query.all()
    

    return render_template('challenge/view_all.htm', challenges=challenges)

""" API's """
@blueprint.route('/api/fetch_all_challenges', methods=['GET', 'POST'])
def fetch_all():
    # if not(GroupPermissionAPI.can_write('challenges')):
        # abort(403)

    challenges = ChallengeAPI.fetch_all_challenges()

    return jsonify(challenges = [challenge.serialize for challenge in challenges])

@blueprint.route('/api/fetch_challenge', methods=['GET', 'POST'])
@blueprint.route('/api/fetch_challenge/<challenge_id>', methods=['GET', 'POST'])
def fetch_question(challenge_id=None):
    # if not(GroupPermissionAPI.can_write('challenges')):
        # abort(403)
        
    if challenge_id is None:
        return jsonify({'error': 'No "challenge_id" argument given'})

    challenge = ChallengeAPI.fetch_challenge(challenge_id)

    return jsonify(challenges = challenge.serialize)

@blueprint.route('/api/create_challenge', methods=['GET', 'POST'])
def create_challenge(challenge_id=None):
    # if not(GroupPermissionAPI.can_write('challenges')):
    #     abort(403)

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
        start_date = datetime.strptime(request.args.get('start_date'), '%d-%m-%Y').date()
    else:
        return "Error, no 'start_date' given"
    
    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%d-%m-%Y').date()
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

    return ChallengeAPI.create_challenge(name, description, hint, start_date, end_date,
                        parent_id, weight, type, answer)

@blueprint.route('/api/new_submission', methods=['GET', 'POST'])
def new_submission(challenge_id=None):
    # if not(GroupPermissionAPI.can_read('challenges')):
        # abort(403)

    if request.args.get('challenge_id'):
        challenge_id = request.args.get('challenge_id')
    else:
        return "Error, no 'challenge_id' given"
    
    if request.args.get('submission'):
        submission = request.args.get('submission')
    else:
        return "Error, no 'submission' given"

    new_submission = ChallengeAPI.create_submission(challenge_id=challenge_id, user_id=current_user.id,
                 submission=submission, image_path=None)

    challenge = ChallengeAPI.fetch_challenge(challenge_id)
    return ChallengeAPI.validate_question(new_submission, challenge)

