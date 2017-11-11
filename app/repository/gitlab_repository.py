from urllib.parse import urlencode


def create_gitlab_issue(session, data):
    url = 'https://gitlab.com/api/v4/projects/4110282/issues'
    url += '?' + urlencode(data)
    return session.post(url)
