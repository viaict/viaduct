from flask import request, url_for, redirect as flask_redirect
from urllib.parse import urlparse, urljoin


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def redirect_back(default='home.home', **values):
    return flask_redirect(get_safe_redirect_url(default, **values))


def get_safe_redirect_url(default='home.home', **values):
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target
    return url_for(default, **values)
