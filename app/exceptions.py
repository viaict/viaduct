class ResourceNotFoundException(Exception):
    def __init__(self, resource, identifier):
        self.resource = resource
        self.identifier = identifier

    def __str__(self):
        return ("Could not find resource " + str(self.resource) +
                " identified by " + str(self.identifier))


class BusinessRuleException(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.detail = args[0] if args else ''


class ValidationException(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.detail = args[0] if args else ''
