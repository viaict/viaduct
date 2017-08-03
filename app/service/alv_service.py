from flask_babel import _

from app.repository import alv_repository
from app.views.errors import ResourceNotFoundException


def save(alv):
    alv_repository.save(alv)


def set_alv_presidium(alv, new_presidium_users=None):
    if new_presidium_users is None:
        new_presidium_users = []

    alv_repository.delete_presidium(alv)
    for presidium in new_presidium_users:
        presidium.alv = alv
    alv_repository.insert_presidium(alv, new_presidium_users)


def find_by_id(alv_id, include_presidium, include_documents):
    return alv_repository.find_by_id(alv_id,
                                     include_presidium=include_presidium,
                                     include_documents=include_documents)


def get_by_id(alv_id, include_presidium=True, include_documents=False):
    alv = find_by_id(alv_id, include_presidium, include_documents)
    if not alv:
        raise ResourceNotFoundException("alv")
    return alv


def format_presidium(alv):
    print("LOL")
    if not alv.chairman and not alv.secretary:
        return _("No presidium")

    rv = []

    if alv.chairman:
        print("LOL2")
        print(str(alv.chairman))
        rv.append(str(alv.chairman))
    if alv.secretary:
        print("LOL2")
        rv.append(str(alv.secretary))

    return _("Presidium: ") + ", ".join(rv)
