class DetailedException(Exception):
    def __init__(self, id, status=500, title="Internal Server Error",
                 type_="about:blank"):
        self.id = id
        self.title = title
        self.type_ = type_
        self.status = status


class ResourceNotFoundException(DetailedException):
    def __init__(self, resource, identifier, **kwargs):
        super(ResourceNotFoundException, self).__init__(
            id=1, status=464, title="Not Found", **kwargs)
        self.resource = resource
        self.identifier = identifier

    def __str__(self):
        return ("Could not find resource '" + str(self.resource) +
                "' identified by '" + str(self.identifier)) + "'"


class BusinessRuleException(DetailedException):
    def __init__(self, detail, **kwargs):
        super(BusinessRuleException, self).__init__(
            id=2, status=409, title="Business Rule Violation", **kwargs)
        self.detail = detail

    def __str__(self):
        return ("A business rule was violated in the request. " +
                str(self.detail))


class ValidationException(DetailedException):
    def __init__(self, details, **kwargs):
        super(ValidationException, self).__init__(
            id=3, status=400, title="Validation Error", **kwargs)
        self.details = details

    def __str__(self):
        return ("The request was not according to semantic rules. " +
                str(self.details))


class AuthorizationException(DetailedException):
    def __init__(self, details, **kwargs):
        super(AuthorizationException, self).__init__(
            id=4, status=403, title="Unauthorized", **kwargs)
        self.details = details

    def __str__(self):
        return ("You are not authorized for this operation. " +
                str(self.details))
