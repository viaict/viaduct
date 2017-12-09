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


class DuplicateResourceException(Exception):
    def __init__(self, resource, identifier):
        self.identifier = identifier
        self.resource = resource

    def __str__(self):
        return "Duplicate resource '" + str(self.resource) + \
               "' identified by '" + str(self.identifier) + "'"
