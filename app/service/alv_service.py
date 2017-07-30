from app.repository import alv_repository


def create(alv):
    alv_repository.create(alv)


def update(alv):
    alv_repository.update(alv)


def set_alv_presidium(alv, new_presidium_users=None):
    if new_presidium_users is None:
        new_presidium_users = []

    alv_repository.delete_presidium(alv)
    for presidium in new_presidium_users:
        presidium.alv = alv
    alv_repository.insert_presidium(alv, new_presidium_users)


def find_by_id(alv_id, include_presidium=True, include_documents=False):
    return alv_repository.find_by_id(alv_id,
                                     include_presidium=include_presidium,
                                     include_documents=include_documents)
