# Version 2.0.2.2
Versioning works as follows: vSYSTEM.FEATURE.IMPROVEMENT.BUG-/HOTFIX

#Viaduct (Opensourced, yeah)
## Tutorial
See [tutorial](TUTORIAL.md).

## Setup:
OS Packages: python3, sqlite, pip, virtualenv, mysql-server, git-flow,
python3-dev, libffi-dev
Install with your favorite packagemanager.

Get the secret via config files with secrets for the server:
```bash
git submodule init
git submodule update
```
Set up the awesome hooks:
```bash
cd .git/hooks
ln -s ../../secrets/post-* .
cd ../..
.git/hooks/post-merge
```

Setup git-flow:
```bash
git flow init
```
The first one is master, the second develop after that just keep hitting return.

Before installing the Python dependencies, you have to install libjpeg-dev:

    sudo apt-get install libjpeg-dev

Python dependencies are in `requirements.txt`. Install through pip. Usage of virtual environments is recommended:

	virtualenv venv/ -p /usr/bin/python3
	. venv/bin/activate
	pip install -r requirements.txt

Build dependencies are for ruby and npm:
* Install Ruby gems
    - Install Ruby
    - `gem install bundler`
    - `bundle install` (if that does not work try this:
      http://guides.rubygems.org/faqs/#user-install)

* Install Grunt build dependencies
    - Install nodeJS (with npm included)
    - `(sudo) npm install -g grunt-cli`
    - `npm install`

* Get a live database of the via server by asking the coordinator.
Use it by database by installing mysql and running:
    - `(sudo) mysql -u root -p < mysqlinit.sql`
    - `(sudo) mysql -u root -p < database.sql`

Run site with:

    `./watch.sh`

For troubleshooting tips, see bottom of document.

##Language
All code shall be written in **English**, translations should be added through
Babel. After writing code with **English** strings, add their **Dutch**
translations.

Adding a language through Babel:
    python babel_init.py [locale]

Updating translation files after creating new pages:
    python babel_update.py
Then, update the **nl** language files for your new strings.

Compiling changed language files:
    python babel_compile.py

Note: lots of pages contain multiple languages, please update and create new
according to this standard.

##Documentation
Documentation according to python's [Docstring Conventions](http://www.python.org/dev/peps/pep-0257/).

##Contributions
Fork project, document nicely. Create pull request with database changes.
Use [PEP8](http://www.python.org/dev/peps/pep-0008/)!!!

#####TROUBLESHOOTING:
- **mysql-python fails with EnvironmentError: mysql_config not found**
Install libmysqlclient-dev
- **error: command 'x86_64-linux-gnu-gcc' failed with exit status 1**
Install python-dev.
- **IOError: [Errno 13] Permission denied: '/home/username/.pip/pip.log'**
sudo chown username:username /home/username/.pip/pip.log
- **ImportError: No module named config** Make sure you have a config file (see `config.py.sample`)
