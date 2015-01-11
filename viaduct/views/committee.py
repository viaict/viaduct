from flask import Blueprint, abort, request, flash, redirect, url_for, \
    render_template
from flask.ext.login import current_user

from viaduct import db
from viaduct.models import CommitteeRevision, Page, Group, User, \
    NavigationEntry
from viaduct.api import GroupPermissionAPI, NavigationAPI
from viaduct.forms import CommitteeForm
from viaduct.helpers import flash_form_errors
import viaduct.api.committee as CommitteeAPI

blueprint = Blueprint('committee', __name__)


@blueprint.route('/commissie/', methods=['GET'])
def list():
    revisions = CommitteeAPI.get_alphabetical()
    return render_template('committee/list.htm', revisions=revisions)


@blueprint.route('/edit/commissie/<string:committee>', methods=['GET', 'POST'])
def edit_committee(committee=''):
    if not GroupPermissionAPI.can_write('committee'):
        return abort(403)

    path = 'commissie/' + committee

    page = Page.get_by_path(path)

    data = request.form
    if page:
        revision = page.get_latest_revision()
        form = CommitteeForm(data, revision)
    else:
        revision = None
        form = CommitteeForm()

    form.group_id.choices = [(group.id, group.name) for group in
                             Group.query.order_by(Group.name).all()]

    if len(data) == 0:
        if revision:
            selected_group_id = revision.group_id
        else:
            selected_group_id = form.group_id.choices[0][0]
    else:
        selected_group_id = int(data['group_id'])

    selected_group = Group.query.get(selected_group_id)
    form.coordinator_id.choices = [
        (user.id, user.name) for user in
        selected_group.users.order_by(User.first_name, User.last_name).all()]

    if form.validate_on_submit():
        committee_title = data['title'].strip()

        if not page:
            root_entry = NavigationEntry.query\
                .filter(NavigationEntry.url == url_for('committee.list'))\
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
                    None, 'Commissies', url_for('committee.list'), False,
                    False, root_entry_position)

                db.session.add(root_entry)
                db.session.commit()

            page = Page(path, 'committee')

            # Create a navigation entry for the new committee.
            last_navigation_entry = NavigationEntry.query\
                .filter(NavigationEntry.parent_id == root_entry.id)\
                .first()

            entry_position = 1
            if last_navigation_entry:
                entry_position = last_navigation_entry.position + 1

            navigation_entry = NavigationEntry(
                root_entry, committee_title, '/' + path, False, False,
                entry_position)

            db.session.add(navigation_entry)
            db.session.commit()

            # Sort these navigation entries.
            NavigationAPI.alphabeticalize(root_entry)

            # Assign the navigation entry to the new page (committee).
            page.navigation_entry_id = navigation_entry.id

            db.session.add(page)
            db.session.commit()

        group_id = int(data['group_id'])
        coordinator_id = int(data['coordinator_id'])

        new_revision = CommitteeRevision(
            page, committee_title, data['comment'].strip(),
            current_user.id, data['description'].strip(), group_id,
            coordinator_id, 'interim' in data)

        db.session.add(new_revision)
        db.session.commit()

        flash('De commissie is opgeslagen.', 'success')

        return redirect(url_for('page.get_page', path=path))
    else:
        flash_form_errors(form)

    return render_template('committee/edit.htm', page=page,
                           form=form, path=path)
