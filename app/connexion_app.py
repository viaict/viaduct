import logging
import pathlib
from types import FunctionType  # NOQA

from connexion.apis.flask_api import FlaskApi
from connexion.apps import AbstractApp

logger = logging.getLogger('connexion.app')


class ConnexionFlaskApp(AbstractApp):
    def __init__(self, import_name, app, **kwargs):
        self._flask_app = app
        super().__init__(import_name, FlaskApi, server='flask',
                         debug=app.debug, **kwargs)

    def create_app(self):
        return self._flask_app

    def get_root_path(self):
        return pathlib.Path(self.app.root_path)

    def set_errors_handlers(self):
        """Set all errors handlers of the user framework application."""

        # We don't register any error handle here
        # Instead they are registered in views.errors
        pass

    def add_api(self, specification, **kwargs):
        api = super().add_api(specification, **kwargs)
        self.app.register_blueprint(api.blueprint)
        return api

    def run(self, port=None, server=None, debug=None, host=None, **options):
        """
        Run the application on a local development server.

        :param host: the host interface to bind on.
        :type host: str
        :param port: port to listen to
        :type port: int
        :param server: which wsgi server to use
        :type server: str | None
        :param debug: include debugging information
        :type debug: bool
        :param options: options to be forwarded to the underlying server
        :type options: dict
        """

        # overwrite constructor parameter
        if port is not None:
            self.port = port
        elif self.port is None:
            self.port = 5000

        self.host = host or self.host or '0.0.0.0'

        if server is not None:
            self.server = server

        if debug is not None:
            self.debug = debug

        logger.debug('Starting %s HTTP server..',
                     self.server, extra=vars(self))
        self.app.run(self.host, port=self.port, debug=self.debug, **options)
