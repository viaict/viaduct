from flask import Blueprint, redirect, render_template, url_for, request, \
    jsonify, abort
from flask.ext.login import current_user

from math import ceil
from datetime import date

from viaduct import db, app
from viaduct.models import Nominee, Nomination, Vote
from viaduct.api.module import ModuleAPI


blueprint = Blueprint('elections', __name__, url_prefix='/verkiezing')


def can_nominate():
    td = date.today()
    return td >= app.config['ELECTIONS_NOMINATE_START'] and \
        td < app.config['ELECTIONS_VOTE_START']


def can_vote():
    td = date.today()
    return td >= app.config['ELECTIONS_VOTE_START'] and \
        td <= app.config['ELECTIONS_VOTE_END']


@blueprint.route('/', methods=['GET'])
def main():
    if can_nominate():
        return redirect(url_for('elections.nominate'))
    elif can_vote():
        return redirect(url_for('elections.vote'))

    return redirect(url_for('elections.closed'))


@blueprint.route('/closed/', methods=['GET'])
def closed():
    return render_template('elections/closed.htm')


@blueprint.route('/nomineren/', methods=['GET'])
def nominate():
    if not can_nominate():
        return redirect(url_for('elections.main'))

    if not current_user or not current_user.has_payed:
        return abort(403)

    nominated_ids = [n.nominee.id for n in current_user.nominations.all()]

    nominees = Nominee.query\
        .filter(db.or_(Nominee.valid == True, Nominee.valid == None))\
        .filter(db.not_(Nominee.id.in_(nominated_ids)))\
        .order_by(Nominee.name).all()  # noqa

    return render_template('elections/nominate.htm',
                           title='Docent van het jaar IW/Nomineren',
                           nominations=current_user.nominations,
                           data={'nominees': nominees,
                                 'nominate_url': url_for('elections.'
                                                         'submit_nomination'),
                                 'remove_url': url_for('elections.'
                                                       'remove_nomination')})


@blueprint.route('/nomineren/', methods=['POST'])
def submit_nomination():
    if not can_nominate():
        return jsonify(error='Het nomineren is gesloten')

    if current_user is None:
        return jsonify(error='Je moet ingelogd zijn om een docent te '
                       'nomineren'), 500
    if not current_user.has_payed:
        return jsonify(error='Je moet betaald lid zijn om een docent te '
                       'nomineren'), 500

    nominee_id = request.form.get('id')

    if nominee_id is not None:
        nominee = Nominee.query.get(nominee_id)
    else:
        nominee = Nominee(request.form.get('name'))
        db.session.add(nominee)
        db.session.commit()

    try:
        nominee.nominate(current_user)
    except Exception as ex:
        return jsonify(error=ex.message), 500

    return jsonify()


@blueprint.route('/nomineren/remove/', methods=['POST'])
def remove_nomination():
    if not can_nominate():
        return jsonify(error='Het nomineren is gesloten')

    if current_user is None or not current_user.has_payed:
        return jsonify(error='Je hebt hier helemaal niks te zoeken'), 500

    nomination = Nomination.query.get(request.form.get('id'))

    if nomination.user_id != current_user.id:
        return jsonify(error='Haha, NOPE! Pff, sukkel.'), 500

    db.session.delete(nomination)
    db.session.commit()

    return jsonify()


@blueprint.route('/stemmen/', methods=['GET'])
def vote():
    if not can_vote():
        return redirect(url_for('elections.main'))

    if current_user is None or not current_user.has_payed:
        return abort(403)

    nominees = Nominee.query.filter(Nominee.valid == True)\
        .order_by(Nominee.name).all()  # noqa
    nominee_bound = int(ceil(len(nominees) / 2))

    vote = current_user.vote[0] if current_user.vote else Vote()

    return render_template('elections/vote.htm',
                           title='Docent van het jaar IW/Stemmen',
                           nominees=nominees,
                           nominee_bound=nominee_bound,
                           vote=vote)


@blueprint.route('/stemmen/', methods=['POST'])
def submit_vote():
    if not can_vote():
        return jsonify(error='Het stemmen is gesloten')

    if current_user is None:
        return jsonify(error='Je moet ingelogd zijn om te stemmen'), 500
    if not current_user.has_payed:
        return jsonify(error='Je moet betaald lid zijn om te stemmen'), 500

    nominee_id = request.form.get('nominee_id')
    nominee = Nominee.query.get(nominee_id)

    if not nominee:
        return jsonify(error='Hey zeg, wel eerlijk zijn!'), 500

    try:
        nominee.vote(current_user)
    except Exception as ex:
        return jsonify(error=ex.message), 500

    return jsonify()


@blueprint.route('/admin/', methods=['GET'])
def admin_main():
    return redirect(url_for('elections.admin_nominate'))


@blueprint.route('/admin/nomineren/', methods=['GET'])
def admin_nominate():
    if not ModuleAPI.can_write('elections'):
        return abort(403)

    nominees = Nominee.query.order_by(Nominee.name)

    unchecked_nominees = nominees.filter(Nominee.valid == None).all()  # noqa
    valid_nominees = nominees.filter(Nominee.valid == True).all()  # noqa
    invalid_nominees = nominees.filter(Nominee.valid == False).all()  # noqa

    return render_template('elections/admin_nominate.htm',
                           title='Docent van het jaar IW/Nomineren/Admin',
                           unchecked_nominees=unchecked_nominees,
                           valid_nominees=valid_nominees,
                           invalid_nominees=invalid_nominees,
                           data={'validate_url': url_for('elections.'
                                                         'validate_nominate')})


@blueprint.route('/admin/nomineren/', methods=['POST'])
def validate_nominate():
    if not ModuleAPI.can_write('elections'):
        return jsonify(error='Hey, dit mag jij helemaal niet doen!'), 500

    nominee = Nominee.query.get(request.form.get('id'))
    valid = request.form.get('valid') == 'true'

    nominee.valid = valid
    db.session.commit()

    return jsonify()


@blueprint.route('/admin/stemmen/', methods=['GET'])
def admin_vote():
    if not ModuleAPI.can_write('elections'):
        return abort(403)

    rp = db.engine.execute('SELECT a.*, (SELECT COUNT(*) FROM dvhj_vote b '
                           'WHERE b.nominee_id=a.id) AS votes '
                           'FROM dvhj_nominee a WHERE a.valid=1 '
                           'ORDER BY votes DESC;')

    nominees = []

    def nomi(row):
        return {'id': row[0],
                'created': row[1],
                'modified': row[2],
                'name': row[3],
                'valid': row[4],
                'votes': row[5]}

    while True:
        row = rp.fetchone()
        if row is None:
            break

        nominees.append(nomi(row))

    return render_template('elections/admin_vote.htm',
                           title='Docent van het jaar IW/Stemmen/Admin',
                           nominees=nominees)
