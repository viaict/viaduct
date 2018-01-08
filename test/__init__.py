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

        def __str__(self):
            return 'Any(%s)' % str(cls)

    return Any()


def AnyList(list_cls):  # noqa
    """
    Use during testing to assert call value types as list.

    The function will return an instantiated class that is equal to any
    version of `list(cls)`, for example using string.

        >>> mock = MagicMock()
        >>> mock.func(["str"])
        >>> mock.func.assert_called_once_with(AnyList(str))

    Comparison is done using the isinstance operation.
    :param cls:
    :return:
    """
    class AnyList(list):
        def __eq__(self, other):
            return all(isinstance(item, list_cls) for item in other)

        def __str__(self):
            return "AnyList(%s)" % str(list_cls)
    return AnyList()
