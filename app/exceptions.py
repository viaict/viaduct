class ResourceNotFoundException(Exception):
    def __init__(self, resource, identifier):
        self.resource = resource
        self.identifier = identifier

    def __str__(self):
        return ("Could not find resource " + self.resource +
                " identified by " + self.identifier)


class BusinessRuleException(Exception):
    def __init__(self, detail):
        self.detail = detail
