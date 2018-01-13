#!/usr/bin/env python3
import os
import platform
import re
import subprocess
import sys
import time

import alembic
import alembic.config
import bcrypt
import sqlalchemy
from flask import current_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server, prompt, prompt_pass
from fuzzywuzzy import fuzz
from unidecode import unidecode
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from app import app, init_app, version, Roles
from app.extensions import db, jsglue
from app.models.education import Education
from app.models.group import Group
from app.models.navigation import NavigationEntry
from app.models.role_model import GroupRole
from app.models.user import User

init_app()

migrate = Migrate(app, db)
versionbump = Manager(
    help="Apply a version bump",
    description=("Apply a version bump. "
                 "Versioning works using the following format: "
                 "SYSTEM.FEATURE.IMPROVEMENT.BUG-/HOTFIX"))
administrators = Manager(
    help="Add or remove users from the administrators group",
    description="Add or remove users from the administrators group")

manager = Manager(app, description="Manager console for viaduct")
manager.add_command("runserver", Server())
manager.add_command('db', MigrateCommand)
manager.add_command('versionbump', versionbump)
manager.add_command('admin', administrators)


def prompt_bool(q, default=False):
    yes_choices = ['y', 'yes', '1', 'on', 'true', 't']
    no_choices = ['n', 'n', '0', 'off', 'false', 'f']
    while True:
        if default:
            answer = input(q + " [Y/n]: ") or 'y'

        else:
            answer = input(q + " [y/N]: ") or 'n'
        if answer.lower() in yes_choices:
            return True
        if answer.lower() in no_choices:
            return False


@manager.command
def routes():
    """List all routes present in the application."""
    rules = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue
        methods = rule.methods
        for opt in ['OPTIONS', 'HEAD']:
            if opt in methods:
                methods.remove(opt)

        methods = ', '.join(sorted(rule.methods))
        splitted = rule.endpoint.split('.')
        if len(splitted) != 2:
            blueprint = "(none)"
            function = rule.endpoint
        else:
            blueprint = splitted[0]
            function = splitted[1]
        data = (function, methods, rule.rule)

        if blueprint in rules:
            rules[blueprint].append(data)
        else:
            rules[blueprint] = [data]

    print("\n{:40s} {:30s} {}".format("Function", "Methods", "URL"))
    print("=" * 80)
    for blueprint in sorted(rules.keys()):
        for (endpoint, methods, url) in rules[blueprint]:
            print("{:40s} {:30s} {}".format(blueprint + "." + endpoint,
                                            methods, url))
        print("")


@manager.command
def flaskjs():
    """Generate the javascript file for url_for in javascript."""
    with open('src/js/global/flask.js', 'w', encoding='utf8') as f:
        f.write(jsglue.generate_js())


class EventHandler(FileSystemEventHandler):
    def process(self, event):
        if event.src_path[-5:] == '.jade':
            print("Modified: ", event.src_path)
            self.jade()

    def jade(self):
        if platform.system() == 'Windows':
            subprocess.call(('node node_modules/clientjade/bin/clientjade'
                             ' src/jade/ > src/js/global/jade.js'),
                            shell=True)
        else:
            subprocess.call(('./node_modules/clientjade/bin/clientjade'
                             ' src/jade/ > src/js/global/jade.js'),
                            shell=True)

    def on_created(self, event):
        self.process(event)

    def on_deleted(self, event):
        self.process(event)

    def on_modified(self, event):
        self.process(event)


@manager.command
def jade():
    """Keep track of the jade files and recompile if neccesary."""
    if platform.system() == 'Windows':
        subprocess.call(('node node_modules/clientjade/bin/clientjade'
                         ' src/jade/ > src/js/global/jade.js'),
                        shell=True)
    else:
        subprocess.call(('./node_modules/clientjade/bin/clientjade'
                         ' src/jade/ > src/js/global/jade.js'),
                        shell=True)
    print("Started tracking jade files...")
    path = sys.argv[2] if len(sys.argv) > 2 else '.'
    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()  # HAMMERTIME!
    observer.join()


@manager.command
def mysqlinit():
    """Insert the viaduct user and give it rights for the viaduct db."""
    mysql_user = prompt("User for mysql database", default="root")
    cmd = "mysql -u %s " % mysql_user
    sudo = prompt_bool("Use sudo", default=False)
    if sudo:
        cmd = "sudo " + cmd
    password = prompt_bool("Use password", default=True)
    if password:
        cmd += "-p "
    cmd += "< script/mysqlinit.sql"
    print(cmd)
    subprocess.call(cmd, shell=True)


@manager.command
def test():
    """Run all tests in the test folder."""
    subprocess.call("python -m unittest discover", shell=True)


def _add_group(name):
    try:
        db.session.add(Group(name, None))
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        print("-> Group '{}' already exists.".format(name))


def _add_user(user, catch_error=False, error_msg=None):
    try:
        db.session.add(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        if catch_error:
            print("-> {}.".format(error_msg))
        else:
            raise


def _add_navigation(entries, parent=None):
    for pos, (nl_title, en_title, url, activities, children) \
            in enumerate(entries):
        nav = NavigationEntry(parent, nl_title, en_title, url,
                              False, activities, pos + 1)
        db.session.add(nav)
        db.session.commit()
        _add_navigation(children, nav)


@manager.command
def createdb():
    """Create a new empty database with a single administrator."""

    print("* Creating database schema")

    # Create the database schema
    db.create_all()

    print("* Adding alembic stamp")

    # Create alembic_version table
    migrations_directory = current_app.extensions['migrate'].directory
    config = alembic.config.Config(
        os.path.join(migrations_directory, 'alembic.ini'))
    config.set_main_option('script_location', migrations_directory)
    alembic.command.stamp(config, "head")

    # Add required groups
    print("* Adding administrators' and 'BC' groups")
    _add_group('administrators')
    _add_group('BC')

    # Add educations, which must be present to create the administrator user
    print("* Adding educations")
    education_names = [
        "BSc Informatica",
        "BSc Kunstmatige Intelligentie",
        "BSc Informatiekunde",
        "MSc Information Studies",
        "MSc Software Engineering",
        "MSc System and Network Engineering",
        "MSc Artificial Intelligence",
        "MSc Logic",
        "MSc Computational Science",
        "MSc Computer Science",
        "MSc Medical Informatics",
        "MSc Grid Computing",
        "Other",
        "Minor programmeren",
        "Minor Informatica",
        "Minor Kunstmatige Intelligentie"]

    db.session.bulk_save_objects(Education(name) for name in education_names)
    db.session.commit()

    # Add some default navigation
    print("* Adding default navigation entries")
    navigation_entries = [
        ('via', 'via', '/via', False, [
            ('Nieuws', 'News', '/news/', False, []),
            ('PimPy', 'PimPy', '/pimpy', False, []),
            ('Commissies', 'Committees', '/commissie', False, []),
            ('Admin', 'Admin', '/admin', False, [
                ('Navigatie', 'Navigation', '/navigation', False, []),
                ('Formulieren', 'Forms', '/forms', False, []),
                ('Redirect', 'Redirect', '/redirect', False, []),
                ('Users', 'Users', '/users', False, []),
                ('Groups', 'Groups', '/groups', False, []),
                ('Files', 'Files', '/files', False, [])
            ]),
        ]),
        ('Activiteiten', 'Activities', '/activities', True, [
            ('Activiteiten Archief', 'Activities archive',
             '/activities/archive', False, []),
            ('Activiteiten Overzicht', 'Activities overview',
             '/activities/view', False, [])
        ]),
        ('Vacatures', 'Vacancies', '/vacancies/', False, []),
        ('Tentamenbank', 'Examinations', '/examination', False, []),
        ('Samenvattingen', 'Summaries', '/summary', False, [])
    ]

    _add_navigation(navigation_entries)

    print("* Adding administrator user")

    first_name = prompt("\tFirst name")
    last_name = prompt("\tLast name")

    email_regex = re.compile("^[^@]+@[^@]+\.[^@]+$")
    while True:
        email = prompt("\tEmail")
        if email_regex.match(email):
            break
        print("\tInvalid email address: " + email)

    while True:
        passwd_plain = prompt_pass("\tPassword")
        passwd_plain_rep = prompt_pass("\tRepeat password")
        if passwd_plain == passwd_plain_rep:
            break
        print("\tPasswords do not match")

    passwd = bcrypt.hashpw(passwd_plain.encode('utf-8'), bcrypt.gensalt())
    admin = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=passwd,
        education_id=Education.query.first().id)
    admin.has_paid = True
    _add_user(admin, True,
              "A user with email '{}' already exists".format(email))

    # Add admin user to administrators group
    admin_group = Group.query.filter_by(name='administrators').first()
    admin_group.add_user(admin)
    db.session.commit()

    roles = []
    for role in Roles:
        group_role = GroupRole()
        group_role.group_id = admin_group.id
        group_role.role = role
        roles.append(group_role)

    # Grant read/write privilege to administrators group on every module
    db.session.bulk_save_objects(roles)
    db.session.commit()

    print("Done!")


def _get_current_version():
    current_version_str = version
    m = re.match(r'^v(\d+).(\d+).(\d+).(\d+)$', current_version_str)
    if not m:
        raise ValueError('Invalid version in app module: {}'.format(
            current_version_str))

    return tuple(int(m.group(i)) for i in range(1, 5))


def _bump_version(current_version, new_version):
    print("Current version: \tv{}.{}.{}.{}".format(*current_version))
    print("New version: \t\tv{}.{}.{}.{}".format(*new_version))

    answer = prompt_bool("Continue?")
    if not answer:
        print("Aborted")
        return

    readme_version_regex = re.compile(r'^# Viaduct v\d+.\d+.\d+.\d+')
    init_version_regex = re.compile(
        r"^version\s+=\s+'v\d+.\d+.\d+.\d+'")
    readme_newversionline = '# Viaduct v{}.{}.{}.{}'.format(*new_version)
    init_newversionline = "version = 'v{}.{}.{}.{}'".format(*new_version)

    _bump_file('README.md', readme_version_regex,
               readme_newversionline)
    _bump_file('app/__init__.py', init_version_regex,
               init_newversionline)


def _bump_file(fn, regex, newversion_line):
    print("Bumping {}".format(fn))
    with open(fn, 'r+') as f:
        match = None
        pos = 0
        for _line in f:
            line = _line[:-1]
            match = regex.match(line)
            if match:
                break
            pos += len(_line)

        if match:
            f.seek(pos)
            f.write(newversion_line + "\n")
        else:
            raise ValueError('No version found in file {}'.format(fn))


@versionbump.command
def hotfix():
    """Increment one on BUG-/HOTFIX level."""
    current_version = _get_current_version()
    (s, f, i, b) = current_version
    new_version = (s, f, i, b + 1)
    _bump_version(current_version, new_version)


@versionbump.command
def improvement():
    """Increment one on IMPROVEMENT level."""
    current_version = _get_current_version()
    (s, f, i, b) = current_version
    new_version = (s, f, i + 1, 0)
    _bump_version(current_version, new_version)


@versionbump.command
def feature():
    """Increment one on FEATURE level."""
    current_version = _get_current_version()
    (s, f, i, b) = current_version
    new_version = (s, f + 1, 0, 0)
    _bump_version(current_version, new_version)


@versionbump.command
def system():
    """Increment one on SYSTEM level."""
    current_version = _get_current_version()
    (s, f, i, b) = current_version
    new_version = (s + 1, 0, 0, 0)
    _bump_version(current_version, new_version)


def _administrators_action(user_search, remove):
    """Method for adding or removing users in the administrators group."""
    admin_group = Group.query.filter(Group.name == "administrators").first()
    if admin_group is None:
        print("Administrators group does not exist.")
        return

    if user_search.isdigit():
        # Search for user ID
        user_id = int(user_search)
        user_found = User.query.get(user_id)
        if user_found is None or user_id == 0:
            print("User with ID {} does not exist.".format(user_id))
            return
    else:
        # Search in user name
        users = User.query.all()

        maximum = 0
        user_found = None

        # Find user with highest match ratio
        for user in users:
            if user.id == 0:
                continue

            first_name = unidecode(user.first_name.lower().strip())
            last_name = unidecode(user.last_name.lower().strip())

            rate_first = fuzz.ratio(first_name, user_search)
            rate_last = fuzz.ratio(last_name, user_search)

            full_name = first_name + ' ' + last_name
            rate_full = fuzz.ratio(full_name, user_search)

            if (rate_first > maximum or rate_last > maximum or
                    rate_full > maximum):
                maximum = max(rate_first, max(rate_last, rate_full))
                user_found = user

        if user_found is None:
            print("No user found")
            return

    print("Found user: {} (ID {})".format(user_found.name, user_found.id))
    if admin_group in user_found.groups:
        if not remove:
            print("User is already in administrators group")
            return
    elif remove:
        print("User is not in administrators group")
        return

    if remove:
        prompt = "Remove {} from administrators group?".format(user_found.name)
    else:
        prompt = "Add {} to administrators group?".format(user_found.name)

    if prompt_bool(prompt):
        if remove:
            admin_group.delete_user(user_found)
        else:
            admin_group.add_user(user_found)

        db.session.commit()
        print("User successfully {}.".format("removed" if remove else "added"))


@administrators.option(dest='user', help='User ID or name')
def add(user):
    """Add a user to the administrator group."""
    _administrators_action(user, False)


@administrators.option(dest='user', help='User ID or name')
def remove(user):
    """Remove a user from the administrator group."""
    _administrators_action(user, True)


if __name__ == '__main__':
    # Print two newlines after the output of app/__init__.py
    # to make the command's output more readable
    sys.stdout.write("\n\n")

    manager.run()
