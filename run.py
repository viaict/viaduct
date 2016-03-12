#!venv/bin/python2.7

from flask_failsafe import failsafe


@failsafe
def create_app():
    from viaduct import app

    return app

if __name__ == '__main__':
    create_app().run(port=5000)
