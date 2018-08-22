class SearchAPI:
    """
    This module can be used to search through the database.

    A user should supply two things: the query as string,
    and a dictionairy with table names as keys, and a list of
    table columns as values. This dictionairy indicates which
    part of the database is to be search.

    The query will be split on spaces (' '), allowing any of
    the query's words to match on any part of the given part of
    the database.
    """

    @staticmethod
    def search(stack, needle, case_insensitive=True):
        """
        Search generically on specified database tables and columns.

        :param stack is a list of (table, [columns]) tuples.
        :param needle is a string which will be split for seperate words.
        :param case_insensitive indicates case sensitive or insensitive
            search, default is True
        :returns A set of db.models that have matched the queries

        Example:
            > stack = [ (Examination, [Examination.title]),
                (Course, [Course.name]),
                (Education, [Education.name])]
            > needle = "inf"
            > print searchAPI.search(stack, needle)
            set([<app.models.education.Education object at
                0x7f4f5c2ac650>, <app.models.education.Education object
                at 0x7f4f5c2ac710>])
        """
        result_list = []

        for model, columns in stack:
            for word in ["%%%s%%" % word for word in needle.split()]:
                result_list\
                    .extend(model.query.filter(*[column.ilike(word)
                            if case_insensitive else column.like(word)
                                                 for column in columns]).all())

        return set(result_list)
