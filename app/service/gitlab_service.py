import requests

from app import app
from app.repository import gitlab_repository


def create_gitlab_session(token):
    session = requests.Session()
    session.headers.update({'PRIVATE-TOKEN': token})
    return session


def create_gitlab_issue(summary, user_email, description):
    description = "Bug report by: {}\n\n{}".format(user_email, description)
    data = {
        'title': summary,
        'description': description,
        'labels': 'viaduct'
    }
    with create_gitlab_session(app.config['GITLAB_TOKEN']) as s:
        return gitlab_repository.create_gitlab_issue(s, data)
