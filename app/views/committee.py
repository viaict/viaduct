from flask import Blueprint, abort, request, flash, redirect, url_for, \
    render_template
from flask_login import current_user
from flask_babel import _  # gettext

from app import db
from app.models import CommitteeRevision, Page, Group, User, \
    NavigationEntry, PagePermission
from app.utils import ModuleAPI, NavigationAPI
from app.forms import CommitteeForm
from app.utils.forms import flash_form_errors
import app.utils.committee as CommitteeAPI

blueprint = Blueprint('committee', __name__)


@blueprint.route('/commissie/', methods=['GET'])
def list():
    revisions = CommitteeAPI.get_alphabetical()
    return render_template('committee/list.htm', revisions=revisions)


@blueprint.route('/edit/commissie/<string:committee>', methods=['GET', 'POST'])
def edit_committee(committee=''):
    if not ModuleAPI.can_write('committee'):
        return abort(403)

    path = 'commissie/' + committee

    page = Page.get_by_path(path)

    form = request.form
    if page:
        revision = page.get_latest_revision()
        form = CommitteeForm(form, revision)
    else:
        revision = None
        form = CommitteeForm()

    try:
        url_group_id = int(request.args.get('group_id', None))
    except:
        url_group_id = None

    form.group_id.choices = [(group.id, group.name) for group in
                             Group.query.order_by(Group.name).all()]

    if len(request.form) == 0:
        if revision:
            selected_group_id = revision.group_id
        elif url_group_id is not None:
            selected_group_id = url_group_id
        else:
            selected_group_id = form.group_id.choices[0][0]
    else:
        selected_group_id = int(form.group_id.data)

    form.group_id.data = selected_group_id

    selected_group = Group.query.get(selected_group_id)
    form.coordinator_id.choices = [
        (user.id, user.name) for user in
        selected_group.users.order_by(User.first_name, User.last_name).all()]

    form.nl_title.data = selected_group.name

    if form.validate_on_submit():
        committee_nl_title = form.nl_title.data.strip()
        committee_en_title = form.en_title.data.strip()

        if not page:
            root_entry_url = url_for('committee.list').rstrip('/')
            root_entry = NavigationEntry.query\
                .filter(NavigationEntry.url == root_entry_url)\
                .first()

            # Check whether the root navigation entry exists.
            if not root_entry:
                last_root_entry = NavigationEntry.query\
                    .filter(NavigationEntry.parent_id == None)\
                    .order_by(NavigationEntry.position.desc()).first()  # noqa

                root_entry_position = 1
                if last_root_entry:
                    root_entry_position = last_root_entry.position + 1

                root_entry = NavigationEntry(
                    None, 'Commissies', 'Committees', root_entry_url, False,
                    False, root_entry_position)

                db.session.add(root_entry)
                db.session.commit()

            page = Page(path, 'committee')

            # Never needs payed.
            page.needs_payed = False

            # Create a navigation entry for the new committee.
            last_navigation_entry = NavigationEntry.query\
                .filter(NavigationEntry.parent_id == root_entry.id)\
                .first()

            entry_position = 1
            if last_navigation_entry:
                entry_position = last_navigation_entry.position + 1

            navigation_entry = NavigationEntry(
                root_entry, committee_nl_title, committee_en_title, '/' + path,
                False, False, entry_position)

            db.session.add(navigation_entry)
            db.session.commit()

            # Sort these navigation entries.
            NavigationAPI.alphabeticalize(root_entry)

            # Assign the navigation entry to the new page (committee).
            page.navigation_entry_id = navigation_entry.id

            db.session.add(page)
            db.session.commit()

            # Assign read rights to all, and edit rights to BC.
            all_group = Group.query.filter(Group.name == 'all').first()
            bc_group = Group.query.filter(Group.name == 'BC').first()

            all_entry = PagePermission(all_group.id, page.id, 1)
            bc_entry = PagePermission(bc_group.id, page.id, 2)

            db.session.add(all_entry)
            db.session.add(bc_entry)
            db.session.commit()
        else:
            # If the committee's title has changed, the navigation needs to be
            # updated. Look for the entry, compare the titles, and change where
            # necessary.
            entry = NavigationEntry.query\
                .filter(NavigationEntry.url == '/' + path).first()
            if entry.title != committee_nl_title:
                entry.title = committee_nl_title
                db.session.add(entry)
                db.session.commit()

        group_id = int(form.group_id.data)
        coordinator_id = int(form.coordinator_id.data)

        # Add coordinator to BC
        bc_group = Group.query.filter(Group.name == "BC").first()
        if bc_group is not None:
            new_coordinator = User.query.filter(
                User.id == coordinator_id).first()
            bc_group.add_user(new_coordinator)

        new_revision = CommitteeRevision(
            page, committee_nl_title, committee_en_title,
            form.comment.data.strip(), current_user.id,
            form.nl_description.data.strip(), form.en_description.data.strip(),
            group_id, coordinator_id, form.interim.data)

        db.session.add(new_revision)
        db.session.commit()

        flash(_('The committee has been saved.'), 'success')

        return redirect(url_for('page.get_page', path=path))
    else:
        flash_form_errors(form)

    return render_template('committee/edit.htm', page=page,
                           form=form, path=path)
