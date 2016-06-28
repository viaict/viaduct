from flask_sqlalchemy import get_debug_queries


def print_queries():
    for query in get_debug_queries():
        print((query.statement, query.parameters))
