#Viaduct

## Tutorial
See [tutorial](TUTORIAL.md).

## Setup:
OS Packages: Python, SQLite, pip, virtualenv.
Install with your favorite packagemanager.

Python dependencies are in `requirements.txt`. Install through pip. Usage of virtual environments is recommended:

	virtualenv venv/
	. venv/bin/activate
	pip install -r requirements.txt
	
A `config.py` file is needed to run the site. Modify `config.py.sample` with your settings and rename the file.

Create a database with:

	python create_db.py

Run site with:

	python run.py
	
For troubleshooting tips, see bottom of document.
	
##Language
Site will be in **Dutch**, documentation and code in **English**.

##Documentation 
Documentation according to python's [Docstring Conventions](http://www.python.org/dev/peps/pep-0257/).

##Contributions
Fork project, document nicely. Create pull request with database changes.

##Indentation
Python, so be nice and indent like everyone else in the project: 4 tabs.  
Local `.vimrc`

	set noexpandtab
	set sw=4 ts=4 sts=0

Global `.vimrc`. Add these lines and the local vimrc will be used in this project

	set exrc            " enable per-directory .vimrc files
  	set secure          " disable unsafe commands in local .vimrc files

#####TROUBLESHOOTING:
- **mysql-python fails with EnvironmentError: mysql_config not found**
Install libmysqlclient-dev
- **error: command 'x86_64-linux-gnu-gcc' failed with exit status 1**
Install python-dev. 
- **IOError: [Errno 13] Permission denied: '/home/username/.pip/pip.log'**
sudo chown username:username /home/username/.pip/pip.log
- **ImportError: No module named config** Make sure you have a config file (see `config.py.sample`)

