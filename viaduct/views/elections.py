from flask import Blueprint, redirect, render_template, url_for, request, \
    jsonify, abort
from flask.ext.login import current_user

from viaduct import db
from viaduct.models import Nominee, Nomination
from viaduct.api.group import GroupPermissionAPI

blueprint = Blueprint('elections', __name__, url_prefix='/verkiezing')


@blueprint.route('/', methods=['GET'])
def main():
    return redirect(url_for('elections.nominate'))


@blueprint.route('/nomineren/', methods=['GET'])
def nominate():
    if current_user is None or not current_user.has_payed:
        return abort(403)

    nominees = Nominee.query.filter(Nominee.valid == True)\
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
    if current_user is None or not current_user.has_payed:
        return jsonify(error='Je hebt hier helemaal niks te zoeken'), 500

    nomination = Nomination.query.get(request.form.get('id'))

    if nomination.user_id != current_user.id:
        return jsonify(error='Haha, NOPE! Pff, sukkel.'), 500

    db.session.delete(nomination)
    db.session.commit()

    return jsonify()


@blueprint.route('/admin/', methods=['GET'])
def admin_main():
    return redirect(url_for('elections.admin_nominate'))


@blueprint.route('/admin/nomineren/', methods=['GET'])
def admin_nominate():
    if not GroupPermissionAPI.can_write('elections'):
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
    if not GroupPermissionAPI.can_write('elections'):
        return jsonify(error='Hey, dit mag jij helemaal niet doen!'), 500

    nominee = Nominee.query.get(request.form.get('id'))
    valid = request.form.get('valid') == 'true'

    nominee.valid = valid
    db.session.commit()

    return jsonify()
