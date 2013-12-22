from flask import Blueprint
from flask import flash, redirect, render_template, request, url_for
from viaduct import db

from viaduct.models.category import Category
from viaduct.models.page import Page

blueprint = Blueprint('category', __name__)

@blueprint.route('/category/', methods=['GET', 'POST'])
@blueprint.route('/category/<cat>', methods=['GET', 'POST'])
def category_page(cat=''):
	is_root = cat == ''

	# No category, load the 'root' category
	if is_root:
		cat = 'ROOT OF ALL CATEGORIES'

		# for pages we want all pages that do not have a category
		pages = filter(lambda x: len(x.categories) == 0, Page.query.all())

		# for categories we want all categories that do not have a super category
		categories = filter(lambda x: len(x.super_categories) == 0,
			Category.query.all())

	# otherwise, simply fetch the info for one category
	else:
		# get the instance of the current category
		category = Category.query.filter(Category.name==cat).first()

		# get the pages for the current category
		pages = category.pages

		# get the sub categories for the current category
		categories = category.sub_categories

	# render the shit out of things
	return render_template('category/view_category.htm',
		is_root=is_root,
		current_category_name=cat,
		pages=pages,
		categories=categories)
