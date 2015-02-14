def serialize_sqla(data, serialize_date=True):
    """
    Serialiation function to serialize any dicts or lists containing sqlalchemy
    objects. This is needed for conversion to JSON format.
    """
    # If has to_dict this is asumed working and it is used
    if hasattr(data, 'to_dict'):
        return data.to_dict(serialize_date=serialize_date)

    # DateTime objects should be returned as isoformat
    if hasattr(data, 'isoformat') and serialize_date:
        return str(data.isoformat())

    # Items in lists are iterated over and get serialized separetly
    if isinstance(data, (list, tuple, set)):
        return [serialize_sqla(item, serialize_date=serialize_date) for item in
                data]

    # Dictionaries get iterated over
    if isinstance(data, dict):
        result = {}
        for key, value in list(data.items()):
            result[key] = serialize_sqla(value, serialize_date=serialize_date)

        return result

    # Try using the built in __dict__ functions and serialize that seperately
    if hasattr(data, '__dict__'):
        return serialize_sqla(data.__dict__, serialize_date=serialize_date)

    # Just hope it works
    return data
