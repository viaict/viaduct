"""
This module contains a set of basic application errors.

Any custom extensions of the exceptions should be a subclass of any of these
classes.
"""
from marshmallow import Schema, fields


class ApplicationException(Exception):
    """Base exception for the application."""

    class ErrorSchema(Schema):
        """Schema for the basic errors."""

        class Meta:
            ordered = ('title', 'message', 'status', 'type', ...)

        status = fields.Integer()
        title = fields.String()
        type = fields.Url(attribute='type_')
        detail = fields.String(attribute='_message')

    status = 500
    title = "Internal Server Error"
    type_ = "about:blank"
    message = "An internal server error occurred."

    def __init__(self, **kwargs):
        self._message = self.message.format(**kwargs)

    def __str__(self):
        return self._message


class ResourceNotFoundException(ApplicationException):
    status = 404
    title = "Not Found"
    message = "Cannot find {resource} identified by {identifier}."

    def __init__(self, resource, identifier):
        super(ResourceNotFoundException, self). \
            __init__(resource=resource, identifier=identifier)


class BusinessRuleException(ApplicationException):
    status = 409
    title = "Conflict"
    message = "A business rule was violated in the request. {details}"

    def __init__(self, details):
        super(BusinessRuleException, self).__init__(details=details)


class DuplicateResourceException(ApplicationException):
    status = 409
    title = "Duplicate Resource"
    message = "Duplicate resource {resource} identified by {identifier}."

    def __init__(self, resource, identifier):
        super(DuplicateResourceException, self) \
            .__init__(resource=resource, identifier=identifier)


class ValidationException(ApplicationException):
    status = 400
    title = "Validation Error"
    message = "The request was not according to semantic rules. {details}"

    def __init__(self, details):
        super(ValidationException, self).__init__(details=details)


class AuthorizationException(ApplicationException):
    status = 403
    title = "Unauthorized"
    message = "You are not authorized for this operation. {details}"

    def __init__(self, details):
        super(AuthorizationException, self).__init__(details=details)
