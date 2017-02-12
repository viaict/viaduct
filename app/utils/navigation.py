# -*- coding: utf-8 -*-
import datetime
import re

from flask import render_template, request, url_for
from app import db
from app.models import Activity, NavigationEntry, Page
from app.utils.page import PageAPI
from app.forms import SignInForm


class NavigationAPI:
    @staticmethod
    def get_navigation_bar():
        entries = NavigationAPI.get_entries(True)
        entries = NavigationAPI.remove_unauthorized(entries)
        login_form = SignInForm()

        return render_template('navigation/view_bar.htm', bar_entries=entries,
                               login_form=login_form)

    @staticmethod
    def _get_entry_by_url(url):
        page = Page.query.filter_by(path=url.lstrip('/')).first()
        if page and page.navigation_entry:
            return page.navigation_entry[0]
        else:
            return NavigationEntry.query.filter_by(url=url).first()

    @staticmethod
    def get_navigation_menu():
        my_path = request.path
        my_path = re.sub(r'(/[0-9]+)?/$', '', my_path)
        print(my_path)

        me = NavigationAPI._get_entry_by_url(my_path)
        if me:
            parent = me.parent
        else:
            parent_path = my_path.rsplit('/', 1)[0]
            page = Page.query.filter_by(path=parent_path).first()
            try:
                parent = page.navigation_entry[0].parent
            except IndexError:
                parent = None

        if parent:
            entries = db.session.query(NavigationEntry)\
                .filter_by(parent_id=parent.id)\
                .order_by(NavigationEntry.position).all()
        else:
            entries = [me] if me else []

        entries = NavigationAPI.remove_unauthorized(entries)

        return render_template('navigation/view_sidebar.htm', back=parent,
                               pages=entries, current=me)

    @staticmethod
    def current_entry():
        my_path = request.path
        temp_strip = my_path.rstrip('0123456789')
        if temp_strip.endswith('/'):
            my_path = temp_strip
        my_path = my_path.rstrip('/')

        return NavigationAPI._get_entry_by_url(my_path)

    @staticmethod
    def parent_entry():
        my_path = request.path

        temp_strip = my_path.rstrip('0123456789')
        if temp_strip.endswith('/'):
            my_path = temp_strip

        my_path = my_path.rstrip('/')

        return db.session.query(NavigationEntry).filter_by(url=my_path)\
            .first()

    @staticmethod
    def order(entries, parent):
        position = 1

        for entry in entries:
            db_entry = db.session.query(NavigationEntry)\
                .filter_by(id=entry['id']).first()

            db_entry.parent_id = parent.id if parent else None
            db_entry.position = position

            NavigationAPI.order(entry['children'], db_entry)

            position += 1

            db.session.add(db_entry)
            db.session.commit()

    @staticmethod
    def get_entries(inc_activities=False):
        entries_all = NavigationEntry.query.order_by(NavigationEntry.position)\
            .all()
        entry_dict = dict((entry.id, entry) for entry in entries_all)

        entries = []
        for entry in entries_all:
            if entry.parent_id is not None:
                parent = entry_dict[entry.parent_id]
                try:
                    parent.children_fast.append(entry)
                except AttributeError:
                    parent.children_fast = [entry]
            else:
                entries.append(entry)

            # Fill in activity lists.
            if entry.activity_list:
                entry.activities = []
                activities = db.session.query(Activity)\
                    .filter(Activity.end_time > datetime.datetime.now())\
                    .order_by("activity_start_time").all()

                for activity in activities:
                    entry.activities.append(
                        NavigationEntry(
                            entry,
                            activity.nl_name,
                            activity.en_name,
                            url_for(
                                'activity.get_activity',
                                activity_id=activity.id),
                            False, False, 0,
                            activity.till_now()))

        return entries

    @staticmethod
    def can_view(entry):
        """
        Check whether the current user can view the entry.

        Note: currently only works with pages.
        """
        if entry.external or entry.activity_list or not entry.page:
            return True
        return PageAPI.can_read(entry.page)

    @staticmethod
    def remove_unauthorized(entries):
        authorized_entries = list(entries)
        for entry in entries:
            if not NavigationAPI.can_view(entry):
                authorized_entries.remove(entry)

        return authorized_entries

    @staticmethod
    def get_navigation_backtrack():
        backtrack = []
        tracker = NavigationAPI.current_entry()
        while tracker:
            backtrack.append(tracker)
            tracker = tracker.parent

        backtrack.reverse()
        return render_template('navigation/view_backtrack.htm',
                               backtrack=backtrack)

    @staticmethod
    def alphabeticalize(parent_entry):
        entries = NavigationEntry.query\
            .filter(NavigationEntry.parent_id == parent_entry.id)\
            .order_by(NavigationEntry.nl_title)\
            .all()

        position = 1

        for entry in entries:
            entry.position = position
            position += 1
