from flask import Blueprint, redirect, render_template, url_for, request, \
    jsonify
from flask.ext.login import current_user

from viaduct import db
from viaduct.models import Nominee

blueprint = Blueprint('elections', __name__, url_prefix='/verkiezing')


@blueprint.route('/', methods=['GET'])
def main():
    return redirect(url_for('elections.nominate'))


@blueprint.route('/nomineren/', methods=['GET'])
def nominate():
    nominees = Nominee.query.order_by(Nominee.name).all()

    return render_template('elections/nominate.htm',
                           title='Docent van het jaar IW/Nomineren',
                           data={'nominees': nominees,
                                 'nominate_url': url_for('elections.submit_nomination')})  # noqa


@blueprint.route('/nomineren/', methods=['POST'])
def submit_nomination():
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
