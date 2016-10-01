from app import app, db, version
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from flask_failsafe import failsafe

import re

manager = Manager(app)


@failsafe
def create_app():
    from app import app

    return app

manager.add_command("runserver", Server())


@manager.command
def routes():
    """List all routes present in the application."""
    rules = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue
        methods = rule.methods
        if 'OPTIONS' in methods:
            methods.remove('OPTIONS')
        if 'HEAD' in methods:
            methods.remove('HEAD')
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

    print("\n\t{:30s} {:30s} {}".format("Function", "Methods", "URL"))
    print("=" * 100)
    for blueprint in sorted(rules.keys()):
        print("Blueprint {}:".format(blueprint))
        for (endpoint, methods, url) in rules[blueprint]:
            print("\t{:30s} {:30s} {}".format(endpoint, methods, url))
        print("")


VersionBump = Manager(
    usage="""Apply a version bump.
Versioning works using the following format:
SYSTEM.FEATURE.IMPROVEMENT.BUG-/HOTFIX
""")


def _get_current_version():
    current_version_str = version
    m = re.match(r'^v(\d+).(\d+).(\d+).(\d+)$', current_version_str)
    if not m:
        raise ValueError('Invalid version in app module: {}'.format(
            current_version_str))

    return tuple(int(m.group(i)) for i in range(1, 5))


def _bump_version(current_version, new_version):
    print("\nCurrent version: \tv{}.{}.{}.{}".format(*current_version))
    print("New version: \t\tv{}.{}.{}.{}".format(*new_version))

    answer = input("Continue? [y/N] ")
    if len(answer) == 0 or answer[0].lower() != 'y':
        print("Abort")
        return

    readme_version_regex = re.compile(r'^# Version \d+.\d+.\d+.\d+')
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


@VersionBump.command
def bugfix():
    """Increment one on BUG-/HOTFIX level."""
    current_version = _get_current_version()
    (s, f, i, b) = current_version
    new_version = (s, f, i, b + 1)
    _bump_version(current_version, new_version)


@VersionBump.command
def improvement():
    """Increment one on IMPROVEMENT level."""
    current_version = _get_current_version()
    (s, f, i, b) = current_version
    new_version = (s, f, i + 1, 0)
    _bump_version(current_version, new_version)


@VersionBump.command
def feature():
    """Increment one on FEATURE level."""
    current_version = _get_current_version()
    (s, f, i, b) = current_version
    new_version = (s, f + 1, 0, 0)
    _bump_version(current_version, new_version)


@VersionBump.command
def system():
    """Increment one on SYSTEM level."""
    current_version = _get_current_version()
    (s, f, i, b) = current_version
    new_version = (s + 1, 0, 0, 0)
    _bump_version(current_version, new_version)


migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
manager.add_command('versionbump', VersionBump)

if __name__ == '__main__':
    manager.run()
