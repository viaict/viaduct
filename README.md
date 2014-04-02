#Viaduct (Opensourced)
## Tutorial
See [tutorial](TUTORIAL.md).

## Setup:
OS Packages: Python, SQLite, pip, virtualenv.
Install with your favorite packagemanager.

Python dependencies are in `requirements.txt`. Install through pip. Usage of virtual environments is recommended:

	virtualenv venv/
	. venv/bin/activate
	pip install -r requirements.txt

A `config.py` file is needed to run the site. Modify `local_config.py` with your settings and rename the file.

Create a database with:

	python create_db.py

Run site with:

	python run.py

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
