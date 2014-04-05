import datetime
import difflib

from flask import Blueprint
from flask import flash, redirect, render_template, request, url_for
from flask.ext.login import current_user
from flask import abort

from viaduct import db
from viaduct.helpers import flash_form_errors
from viaduct.forms import EditPageForm, HistoryPageForm
from viaduct.models import Group
from viaduct.models.page import Page, PageRevision, PagePermission
from viaduct.models.custom_form import CustomForm, CustomFormResult
from viaduct.api.group import GroupPermissionAPI
from viaduct.api.user import UserAPI
from viaduct.api.page import PageAPI
from viaduct.api.category import CategoryAPI
from viaduct.models.activity import Activity

blueprint = Blueprint('page', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<path:path>', methods=['GET', 'POST'])
def get_page(path=''):
	revisions = []

	custom_form = False
	is_main_page = False

	if path == '' or path == 'index':
		paths = ['laatste_bestuursblog', 'activities', 'twitter', 'contact']
		is_main_page = True
	else:
		paths = [path]

	for path in paths:
		page = Page.query.filter(Page.path == path).first()

		if not page:
			page = Page('')

		if page.revisions.count() > 0:
			revision = page.revisions.order_by(PageRevision.id.desc()).first()

			# Check if there is a custom_form
			if revision.form_id:
				custom_form = CustomForm.query.get(revision.form_id)

				if custom_form:

					# Count current attendants for "reserved" message
					entries = CustomFormResult.query\
						.filter(CustomFormResult.form_id == revision.form_id)
					custom_form.num_attendants = entries.count()

					# Check if the current user has already entered data in
					# this custom form.
					if current_user and current_user.id > 0:
						form_result = CustomFormResult.query \
							.filter(CustomFormResult.form_id ==
									revision.form_id) \
							.filter(CustomFormResult.owner_id ==
									current_user.id).first()

						if form_result:
							custom_form.form_data = form_result.data\
								.replace('"', "'")
							custom_form.form_info = 'Je hebt het formulier '\
													'ingevuld. Je kan je '\
													'inzending wel aanpassen!'
						else:
							if custom_form.num_attendants >=\
									custom_form.max_attendants:
								custom_form.form_info = 'Het formulier is '\
														'vol, als je je nu '\
														'inschrijft kom je '\
														'op de reserve lijst!'
							else:
								custom_form.form_info = 'Er zijn op het '\
														'moment %s '\
														'inschrijvingen' %\
									(custom_form.num_attendants)

					# Add custom form to revision
					revision.custom_form = custom_form

			if not current_user:
				if not UserAPI.can_read(page):
					if not path == 'activities':
						abort(403)
			elif revision.author and current_user and\
					not revision.author.id == current_user.id:
				if not UserAPI.can_read(page):
					if not path == 'activities':
						abort(403)
		else:
			revision = PageRevision(page, current_user,
									'Oh no! It looks like you have found a '
									'dead Link!', '<img class="linkimg404" src="/static/img/404.png">'
									'', True)

		class struct(object):
			pass

		# TODO this data object is for the front page -> Seperate logic for
		# normal pages and index page.
		data = struct()
		data.is_main_page = is_main_page
		data.title = revision.title
		data.content = revision.content
		data.filter_html = revision.filter_html
		data.path = path
		data.page = page

		revisions.append(data)

		# Allow revision path for normal page templates
		revision.path = path

	if is_main_page:
		activities = Activity.query \
			.filter(Activity.end_time > datetime.datetime.now()) \
			.order_by(Activity.start_time.asc())\
			.paginate(1, 12, False)
		return render_template('page/get_page.htm', revisions=revisions, activities=activities)
	else:
		return render_template('page/view_single.htm', page=revision)


@blueprint.route('/history/', methods=['GET', 'POST'])
@blueprint.route('/history/<path:path>', methods=['GET', 'POST'])
def get_page_history(path=''):
	#if not current_user.is_authenticated():
	#	return get_error_page()

	form = HistoryPageForm(request.form)

	page = Page.query.filter(Page.path == path).first()

	if not UserAPI.can_write(page):
		abort(403)

	if not page:
		page = Page('')

	if page.revisions.count() > 0:
		revisions = page.revisions.order_by(PageRevision.id.desc()).all()
	else:
		revisions = None

	form.previous.choices = [(revision.id, '') for revision in revisions]
	form.current.choices = [(revision.id, '') for revision in revisions]

	if form.validate_on_submit():
		previous = request.form['previous']
		current = request.form['current']

		previous_revision = page.revisions\
			.filter(PageRevision.id == previous).first()
		current_revision = page.revisions\
			.filter(PageRevision.id == current).first()

		diff = difflib.HtmlDiff()\
			.make_table(previous_revision.content.splitlines(),
						current_revision.content.splitlines())

		return render_template('page/compare_page_history.htm', diff=diff)

	return render_template('page/get_page_history.htm', form=form,
						revisions=zip(revisions, form.previous,
									form.current))


@blueprint.route('/edit/', methods=['GET', 'POST'])
@blueprint.route('/edit/<path:path>/', methods=['GET', 'POST'])
def edit_page(path=''):
	class struct(object):
		pass

#	if not current_user.is_authenticated():
#		return get_error_page()

	# find current page
	page = Page.query.filter(Page.path == path).first()

	data = None

	# if the current is page is not found, show the edit form to make a new
	# page.
	new_page = True
	if page:
		new_page = False
		revision = page.revisions.order_by(PageRevision.id.desc()).first()

		if revision:
			if not current_user:
				abort(403)
			if revision.author and current_user and\
					not revision.author.id == current_user.id:
				if not UserAPI.can_write(page):
					abort(403)

			# data is used on the front page
			data = struct()
			data.title = revision.title
			data.content = revision.content
			data.filter_html = revision.filter_html
			data.needs_payed = page.needs_payed
			data.path = path
			data.form_id = revision.form_id
	elif not(GroupPermissionAPI.can_write('page')):
		return abort(403)

	# show edit page form
	form = EditPageForm(request.form, obj=data)

	# Add a dropdown select for available custom_forms
	form.form_id.choices =\
		[(c.id, c.name) for c in CustomForm.query.order_by('name')]

	# Set default to "No form"
	form.form_id.choices.insert(0, (0, 'Geen formulier'))

	# used to set permissions later in the code
	groups = Group.query.all()

	# on page submit (edit or create)
	if form.validate_on_submit():
		title = request.form['title'].strip()
		content = request.form['content'].strip()
		comment = request.form['comment'].strip()

		#if 'filter_html' in request.form:
		#	filter_html = False
		#else:
		#	filter_html = True
		filter_html = 'filter_html' in request.form

		# if there was no page we want to create an entire new page (and not
		# just a revision)
		if not page:
			page = Page(path)

		page.needs_payed = 'needs_payed' in request.form

		db.session.add(page)
		db.session.commit()

		# Enter permission in db
		for form_entry, group in zip(form.permissions, groups):
			permission_entry = PagePermission.query\
				.filter(PagePermission.group_id == group.id,
						PagePermission.page_id == page.id).first()

			permission_level = form_entry.select.data

			if permission_entry:
				permission_entry.set_permission(permission_level)
			else:
				permission_entry = PagePermission(group.id, page.id,
												permission_level)

			db.session.add(permission_entry)
			db.session.commit()

		# Set a custom_form id
		form_id = int(request.form['form_id'])
		if not form_id:
			form_id = None
		#form_id = request.get('form_id', None)

		# extract category from content and update stuff!
		CategoryAPI.update_categories_from_content(content, page)

		# create the revision (the first if is an entire new page)
		revision = PageRevision(page, current_user, title, content, comment,
								filter_html,
								timestamp=datetime.datetime.utcnow(),
								form_id=form_id)

		db.session.add(revision)
		db.session.commit()

		flash('The page has been saved.', 'success')

		# redirect newly created page
		return redirect(url_for('page.get_page', path=path))
	# form submission has an error we do not think
	else:
		# TODO: check if we even use this
		for group in groups:
			data = {}
			if page:
				permission = PagePermission.query\
					.filter(PagePermission.group_id == group.id,
							PagePermission.page_id == page.id).first()

				if permission:
					data['select'] = permission.permission

			form.permissions.append_entry(data)
		flash_form_errors(form)

	# no page exist, show edit page or create page
	return render_template('page/edit_page.htm', form=form, new_page=new_page,
						groups=zip(groups, form.permissions), path=path)


@blueprint.route('/remove/<path:path>/', methods=['GET'])
def remove_page(path):
	if not GroupPermissionAPI.can_write('page'):
		return abort(403)

	if PageAPI.remove_page(path):
		flash('The page has been removed.', 'success')
	else:
		flash('The page you are trying to remove does not exist.', 'error')

	return redirect('/')
