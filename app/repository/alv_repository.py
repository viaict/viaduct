from sqlalchemy.orm import joinedload

from app import db
from app.models.alv_model import Alv, AlvPresidium


def create(alv):
    db.session.add(alv)
    db.session.commit()
    return alv


def update(alv):
    db.session.commit()
    return alv


def find_by_id(alv_id, include_presidium=True, include_documents=False):
    q = db.session.query(Alv) \
        .filter_by(id=alv_id)
    if include_presidium:
        q = q.options(joinedload('presidium'))
    if include_documents:
        q = q.options(joinedload('documents'))

    # THIS IS VERY IMPORTANT TO GUARANTEE QUERY SPEED.
    # q = q.options(raiseload('*'))
    return q.one_or_none()


def delete_presidium(alv):
    db.session.query(AlvPresidium) \
        .filter(AlvPresidium.alv_id == alv.id) \
        .delete(synchronize_session='fetch')
    db.session.commit()


def insert_presidium(alv, new_presidium):
    db.session.add_all(new_presidium)
    db.session.commit()
