def Any(cls):  # noqa
    """
    Use during testing to assert call value type.

    The function will return an instantiated class that is equal to any
    version of `cls`, for example using string.

        >>> mock = MagicMock()
        >>> mock.func("str")
        >>> mock.func.assert_called_once_with(Any(str))

    Comparison is done using the isinstance operation.
    """

    class Any(cls):
        def __eq__(self, other):
            return isinstance(other, cls)

    return Any()
