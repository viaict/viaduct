from viaduct.models.category import Category
from viaduct import db

import re


class CategoryAPI:

    @staticmethod
    def update_categories_from_content(content, page):
        """ Parses the string content for categories.

        The found categories in the content are processed as followed:
        * Existing categories are updated to save the path.
        * Unknown categories are created and save the path.

        Categories which had this page, but are not found in the content are
        updated if the category has other pages and deleted if they have no
        other pages left.

        Categories are indicated in the text as followed:
            [[Category:Category name]]"""

        # we shall store all found categories in this list
        found_categories = []

        # obtain categories in which the page was previously present (used
        # later on)
        previous_categories = filter(lambda x: page in x.pages,
                                     Category.query.all())

        # FIXME: compile this regex only once for awesomeness
        pattern = re.compile("\[\[Category:[a-zA-Z0-9 _]+\]\]")
        matches = re.findall(pattern, content)

        # loop over all matches!
        for match in matches:
            # if the regex is correct then the correct name should be parsed!!
            category_name = match[11:-2].strip()
            is_new, category = CategoryAPI.get_category_instance(category_name)

            # if the page was not yet included in the category we want to add
            # it
            if page not in category.pages:
                category.pages.append(page)
                is_new = True

            # if the instance is changed or new we shall update the database
            if is_new:
                db.session.add(category)
                db.session.commit()

            # store the category in a list so we can work with it later
            found_categories.append(category)

        print('fffooooooooound categories', found_categories)

        # check if previous categories are still present in the content, or
        # delete them otherwise
        absent_categories = filter(lambda x: x not in found_categories,
                                   previous_categories)
        for absent_category in absent_categories:
            absent_category.pages.remove(page)

            print("fjdsaklfjdsakfjdsaklfjdksal", absent_category.pages)
            if len(absent_category.pages) == 0:
                db.session.delete(absent_category)
            else:
                db.session.add(absent_category)

            db.session.commit()

    @staticmethod
    def get_category_instance(category_name):
        """ Obtains a category instance from a name.

        This is either retrieved from an existing category out of the database
        or a new instance is created from the database. No commits to the
        database are executed in this function.

        Returns a tuple. A boolean is stored in the first index, this boolean
        indicates if the instance is new (And should be commited to the db) or
        not. The second index stores the instance of the category."""

        category = Category.query.filter(Category.name == category_name)\
            .first()
        if category:
            return False, category

        return True, Category(category_name)
