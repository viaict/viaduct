from flask_failsafe import failsafe


@failsafe
def create_app():
    from app import init_app

    return init_app(debug=True)


if __name__ == '__main__':
    create_app().run(host="0.0.0.0", port=5000, debug=True)
