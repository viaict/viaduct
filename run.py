from flask_failsafe import failsafe


@failsafe
def create_app():
    from app import init_app
    connexion_patched_app = init_app()

    return connexion_patched_app


if __name__ == '__main__':
    create_app().run(port=5000)
