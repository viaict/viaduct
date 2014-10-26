# Version.
1.3

#Viaduct (Opensourced, yeah)
## Tutorial
See [tutorial](TUTORIAL.md).

## Setup:
OS Packages: Python, SQLite, pip, virtualenv, mysql.
Install with your favorite packagemanager.

Python dependencies are in `requirements.txt`. Install through pip. Usage of virtual environments is recommended:

	virtualenv venv/
	. venv/bin/activate
	pip install -r requirements.txt

A `config.py` file is needed to run the site. Modify `local_config.py` with your settings and rename the file.

Build dependencies are for ruby and npm:
* Install Ruby gems
    - Install Ruby
    - `cp def_config.rb config.rb`
    - `gem install bundler`
    - `bundle install` (if that does not work try this:
      http://guides.rubygems.org/faqs/#user-install)

* Install Grunt build dependencies
    - Install nodeJS (with npm included)
    - `(sudo) npm install -g grunt-cli`
    - `npm install`

Create a temporary database with:
    - `(sudo) mysql -u root -p < mysqlinit.sql`
	- `python create_db.py`

Using a live database by installing mysql and running:
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
