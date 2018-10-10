from flask_restful import Resource


class UserAvatarResource(Resource):

    def get(self):
        """Send out the users avatar file."""
        return NotImplementedError()

    def put(self):
        """Put in a new avatar for the user."""
        return NotImplementedError()
