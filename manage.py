from app import app, db, version, js_glue
from flask_script import Manager, Server, prompt
from flask_migrate import Migrate, MigrateCommand
from flask_failsafe import failsafe


from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import time
import re
import sys
import subprocess
import platform


@failsafe
def create_app():
    from app import app

    return app

migrate = Migrate(app, db)
versionbump = Manager(usage=("Apply a version bump."
                             "Versioning works using the following format: "
                             "SYSTEM.FEATURE.IMPROVEMENT.BUG-/HOTFIX"))
manager = Manager(app, usage=("Manager console for viaduct"))
manager.add_command("runserver", Server())
manager.add_command('db', MigrateCommand)
manager.add_command('versionbump', versionbump)


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
    """Genereate the javascript file for url_for in javascript."""
    with open('src/js/global/flask.js', 'w', encoding='utf8') as f:
        f.write(js_glue.generate_js())


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


if __name__ == '__main__':
    manager.run()
