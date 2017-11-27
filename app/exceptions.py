class ResourceNotFoundException(Exception):
    def __init__(self, resource, identifier):
        self.resource = resource
        self.identifier = identifier

    def __str__(self):
        return ("Could not find resource " + str(self.resource) +
                " identified by " + str(self.identifier))


class BusinessRuleException(Exception):
    def __init__(self, detail):
        self.detail = detail


class InvalidArgumentsException(Exception):
    def __init__(self, details):
        self.details = details


class ValidationException(Exception):
    def __init__(self, details):
        self.details = details


class AuthorizationException(Exception):
    def __init__(self, details):
        self.details = details
