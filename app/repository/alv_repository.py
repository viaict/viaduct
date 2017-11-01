from sqlalchemy.orm import joinedload, raiseload

from app import db
from app.models.activity import Activity
from app.models.alv_model import Alv, AlvDocument, AlvDocumentVersion
from app.models.user import User


def create_document():
    return AlvDocument()


def create_document_version():
    return AlvDocumentVersion()


def save(alv):
    db.session.add(alv)
    db.session.commit()
    return alv


def save_document(alv_document):
    db.session.add(alv_document)
    db.session.commit()


def save_document_version(alv_doc_version):
    db.session.add(alv_doc_version)
    db.session.commit()


def find_all_alv():
    return db.session.query(Alv).order_by(Alv.date.desc()).all()


def find_alv_by_id(alv_id, include_presidium=True, include_documents=False):
    """Retrieve ALV from the database, with the minimal foreign key info."""
    q = db.session.query(Alv) \
        .filter_by(id=alv_id) \
        .options(joinedload(Alv.activity)
                 .load_only(Activity.nl_name, Activity.en_name,
                            Activity.nl_description, Activity.en_description,
                            Activity.start_time))

    if include_presidium:
        q = q.options(joinedload(Alv.chairman)
                      .load_only(User.first_name, User.last_name),
                      joinedload(Alv.secretary)
                      .load_only(User.first_name, User.last_name))
    if include_documents:
        q = q.options(joinedload(Alv.documents)
                      .joinedload(AlvDocument.versions)
                      .subqueryload(AlvDocumentVersion.file))

    q = q.options(raiseload('*'))
    return q.one_or_none()


def find_alv_document_by_id(alv_document_id):
    return db.session.query(AlvDocument) \
        .filter_by(id=alv_document_id) \
        .options(raiseload('*')) \
        .one_or_none()


def delete_alv(alv):
    db.session.delete(alv)
    db.session.commit()
