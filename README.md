# Viaduct v2.11.0.0
Versioning works as follows: vSYSTEM.FEATURE.IMPROVEMENT.BUG-/HOTFIX

## Tutorial

See [tutorial](TUTORIAL.md).


## Setup:

 - Primary development is located at [gitlab.com](https://gitlab.com/studieverenigingvia/viaduct).


### Python environment

Development can be done using only `docker` and `docker-compose`, then you can 
 skip this step and the ruby and node setup.

For the Python dependencies, usage of virtual environments is recommended.
All dependencies are listed in `requirements.in`.
Using `pip-tools` we compile a list of the dependencies with pinned versions,
which are contained in `requirements.txt`.
To install the dependencies in a virtual environment, run the following commands:

```bash
virtualenv venv/ -p /usr/bin/python3
. venv/bin/activate
pip install pip-tools
pip-sync
```

### Configuration files

The config of viaduct is done using the database. To create an initial database
with basic settings configured run:

```bash
docker-compose run --rm backend python manage.py createdb
```

To check that all code has been written in a correct style, we have server side
hooks installed. To mirror these hooks client side, the hooks need to be
installed. Next to coding style checks, there are also hooks for automatically
compiling translations, updating submodules and compiling Ruby config.

Finally, set up the awesome hooks:

```bash
cd .git
rm -rf hooks
ln -s ../hooks .
cd ..
.git/hooks/post-merge
```


### Install Docker and docker-compose

On most Linux distributions, just install `docker` and `docker-compose` with
your favourite package manager. Add your user to the `docker` group
(`gpasswd -a $USER docker`) so you don't have to use `sudo` all the time.

On macOS, grab [Docker for Mac](https://docs.docker.com/docker-for-mac/) and
install `docker-compose` with your favourite macOS package manager.

On Windows, God help you.


### Ruby and NodeJS tools

**Note:** Only needed for running outside docker

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
    - `docker-compose up database`
    - `psql -h localhost -p 5400 -d viaduct viaduct -f viaduct.sql`

* Add yourself to the administrators group:
   - `python manage.py admin add <your name>`

Run site with:

```bash
docker-compose up
```

For troubleshooting tips, see bottom of document.


## Changes in the database

To make changing the database easy you can use the models to update the actual
database. There are two times you want to do this. The first one is just for
testing your changes locally.
If this is the case use these commands to upgrade your actual database.

This will create a new migration script:

```bash
python manage.py db migrate --message 'revision message'
```

After this script is done you can view it to check if nothing weird is
going to happen when you execute it. After that, just run the server with
docker-compose and it will automatically execute the migration, or run it
manually:

```bash
python manage.py db upgrade
```

If this causes errors, something is wrong. Quite possibly the state of the
database, if you can't fix it yourself ask for help.  If not, you now have an up
to date database.

Once you want to push your changes to develop, this is a bit harder to do
cleanly. Ask for help here, because it differs from time to time what to do.


## Code style

### Language

All code shall be written in **English**, translations should be added through
Babel. After writing code with **English** strings, add their **Dutch**
translations.

Creating strings in python is done using the `(lazy_)gettext` functions.

```python
from flask_babel import _  # in views
from flask_babel import lazy_gettext as _   # in models and forms
```

For updating translation files after creating new pages, first extract the new
translatable strings from the code. Then merge the new extractions with the
existing translations:

```bash
python venv/bin/pybabel extract -F babel.cfg --sort-output -k lazy_gettext \
    -o messages.pot .
python venv/bin/pybabel update -i messages.pot -d app/translations
```

Edit the file `app/translations/nl/LC_MESSAGES/message.po` and add the Dutch
translations for the English strings. Especially look for lines marked "fuzzy",
since they won't be compiled. If the translation is correct, remove the line
marking "fuzzy" and continue.

After that compile the strings to be used in the website:

```bash
python venv/bin/pybabel compile -d app/translations
```

For compiling the strings we have also created a Makefile, that will run these
commands in sequence. Just run `make` to run them.


### Documentation

Documentation according to Python's [Docstring Conventions]
(http://www.python.org/dev/peps/pep-0257/).

Idententation is done using 4 spaces. For vim:

```vim
set expandtab
set sw=4
set ts=4
set sts=0
```


## Contributions

Fork project, document nicely. Create pull request with database changes.
Use [PEP8](http://www.python.org/dev/peps/pep-0008/)!


## Troubleshooting:

- **error: command 'x86_64-linux-gnu-gcc' failed with exit status 1**

  Install python-dev.

- **IOError: [Errno 13] Permission denied: '/home/username/.pip/pip.log'**

  sudo chown username:username /home/username/.pip/pip.log

- **ImportError: No module named config**

  Make sure you have a config file (see `config.py.sample`)
