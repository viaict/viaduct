# Viaduct v2.7.0.4
Versioning works as follows: vSYSTEM.FEATURE.IMPROVEMENT.BUG-/HOTFIX

## Tutorial
See [tutorial](TUTORIAL.md).

## Setup:
 - Mail your public key (`~/.ssh/id_rsa.pub`) to [ict@svia.nl](ict@svia.nl).
 - Clone the repository from `git@svia.nl:viaduct`.

### Requirements
Ubuntu install packages (other OS's should install similar stuff):
```bash
sudo apt-get install python3 python3-pip python-virtualenv mysql-server git-flow npm \
nodejs libjpeg-dev libffi-dev ruby python3-dev
ln -s /usr/bin/nodejs /usr/bin/node
```
### Python environment

Python dependencies are in `requirements.txt`. Install all the requirements
through pip. Usage of virtual environments is recommended. Running the `pip
install` command twice is needed to correctly install the translation binaries
of the Babel package.:

```bash
virtualenv venv/ -p /usr/bin/python3
. venv/bin/activate
pip install -r requirements.txt
pip install -r requirements.txt  # YES DO IT TWICE
```

### Configuration files
The config of viaduct is a private repository that is not pushed to the
github.com servers. Get the submodule with the secret API keys from the server:
```bash
git submodule init
git submodule update
ln -s secrets/local.py config.py
```

To check that all code has been written in a correct style, we have server side
hooks installed. To mirror these hooks client side, the hooks need to be
installed. Next to coding style checks, there are also hooks for automatically
compiling translations, updating submodules and compiling Ruby config.

Set up the awesome hooks:
```bash
cd .git
rm -rf hooks
ln -s ../secrets/hooks .
cd ..
.git/hooks/post-merge
```

### Git Flow

For reference of git flow, please see the [Git flow
cheatsheet](http://danielkummer.github.io/git-flow-cheatsheet/)

We use git flow to streamline the development cycle. Our configuration is as
follows:
 - Branch name for production releases: [master] `Hit [enter]`.
 - Branch name for "next release" development: [develop] `Hit [enter]`.
 - Feature branches? [feature/] `Hit [enter]`.
 - Release branches? [release/] `Hit [enter]`.
 - Hotfix branches? [hotfix/] `Hit [enter]`.
 - Support branches? [support/] `Hit [enter]`.
 - Version tag prefix? [] `Type 'v' and hit [enter]`.

First checkout master, then start the setup of git-flow with the following 
commands. Then, go back to develop:
```bash
git checkout master
git flow init
git checkout develop
```

### Ruby and NodeJS tools
Build dependencies are for ruby and npm:
* Install Ruby gems
    - `gem install bundler`
    - `bundle install` (if that does not work try this:
      http://guides.rubygems.org/faqs/#user-install)

* Install Grunt build dependencies and install JSHint:
    - `sudo npm install -g grunt-cli`
    - `sudo npm install -g jshint`
    - `npm install`

* Get a live database of the via server by asking the coordinator.
Use it by database by installing mysql and running:
    - `python manage.py mysqlinit`
    - `(sudo) mysql -u viaduct -pviaduct < database.sql`

Run site with:

    `./watch.sh`

For troubleshooting tips, see bottom of document.

## Changes in the database
To make changing the database easy you can use the models to update the actual
database. There are two times you want to do this. The first one is just for
testing your changes locally.
If this is the case use these commands to upgrade your actual database.

This will create a new migration script:

```bash
python manage.py db migrate --message 'revision message'`.
```

After this script is done you can view it to check if nothing weird is
going to happen when you execute it. To execute it run:

```bash
python manage.py db upgrade
```

If this causes errors, something is wrong. Quite possibly the state of the
database, if you can't fix it yourself ask for help.  If not, you now have an up
to date database.

Once you want to push your changes to develop, this is a bit harder to do
cleanly. Ask for help here, because it differs from time to time what to do.


## Language
All code shall be written in **English**, translations should be added through
Babel. After writing code with **English** strings, add their **Dutch**
translations.

Creating strings in python is done using the `(lazy_)gettext` functions.

```python
    from flask_babel import _ (In views)
    from flask_babel import lazy_gettext as _ (In models en Forms)
```

For updating translation files after creating new pages, first extract the new
translatable strings from the code. Then merge the new extractions with the
existing translations:

```bash
    python venv/bin/pybabel extract -F babel.cfg --sort-output -k lazy_gettext -o messages.pot .
    python venv/bin/pybabel update -i messages.pot -d app/translations
```

Edit the file `app/translations/nl/LC_MESSAGES/message.po` and add the Dutch
translations for the English strings. Especially look for lines marked "fuzzy",
since they won't be compiled. If the translation is correct, remove the line
marking "fuzzy" and continue.

After that compile the strings to be used
in the website.
```bash
    python venv/bin/pybabel compile -d app/translations
```

For compiling the strings we have also created a make file, that will run these
commands in sequence:

```bash
    make
```

## Documentation
Documentation according to python's [Docstring Conventions](http://www.python.org/dev/peps/pep-0257/).

Idententation is done using 4 spaces. For vim:

```vim
set noexpandtab
set sw=4
set ts=4
set sts=0
```

## Contributions
Fork project, document nicely. Create pull request with database changes.
Use [PEP8](http://www.python.org/dev/peps/pep-0008/)!!!

##### TROUBLESHOOTING:
- **mysql-python fails with EnvironmentError: mysql_config not found**
Install libmysqlclient-dev
- **error: command 'x86_64-linux-gnu-gcc' failed with exit status 1**
Install python-dev.
- **IOError: [Errno 13] Permission denied: '/home/username/.pip/pip.log'**
sudo chown username:username /home/username/.pip/pip.log
- **ImportError: No module named config** Make sure you have a config file (see `config.py.sample`)
