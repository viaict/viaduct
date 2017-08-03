from sqlalchemy.orm import joinedload, raiseload

from app import db
from app.models.alv_model import Alv


def save(alv):
    db.session.add(alv)
    db.session.commit()
    return alv


def find_by_id(alv_id, include_presidium=True, include_documents=False):
    q = db.session.query(Alv) \
        .filter_by(id=alv_id)
    if include_presidium:
        q = q.options(joinedload('chairman'), joinedload('secretary'))
    if include_documents:
        q = q.options(joinedload('documents'))

    # THIS IS VERY IMPORTANT TO GUARANTEE QUERY SPEED.
    q = q.options(raiseload('*'))
    return q.one_or_none()
