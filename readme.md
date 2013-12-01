## INSTALL MODULES:

You will require modules such as these. 

 - flask
 - flask-login
 - flask-sqlalchemy
 - flask-wtf
 - MySQL-python
 - py-bcrypt
 - markdown

However, you will also require the right versions. See Section VIRTUAL ENV for
that. Otherwise you can try installing them with the following commands, but
better just skip to the VIRTUAL ENV chapter.

BUT HOW?
* sudo apt-get install python-dev
* sudo apt-get install libmysqlclient-dev
* sudo apt-get install python-pip
* sudo pip install flask flask-login flask-sqlalchemy flask-wtf
* sudo easy_install -U distribute
* sudo pip install MySQL-python py-bcrypt markdown
* sudo pip install flask-babel
* sudo pip install flask-restful
* sudo pip install validictory

## SYNC CONFIG FILES & RUN SERVER
(in root of the git repo):
ln -s local_config.py config.py
python create_db.py
python run.py

Check localhost:5000
However, your db is still super empty
If stuff still does not work, you might miss modules. Try installing pip again.

https://github.com/jgorset/facepy

## VIRUAL ENV:
het is handig op dit in een virtualenv-omgeving te doen voor als je dingen
helemaal verneukt.
(http://simononsoftware.com/virtualenv-tutorial/)
Voor diegene die het niet weten: met virtualenv kan in je in een omgeving gaan
waarin je kan zeggen wat voor python packages en versies je wilt gebruiken. Zo
kan je ook makkelijk switchen door bijvoorbeeld in de eene versie 0.1 te
installeren en in een andere omgeving 1.4.

	sudo apt-get install virtualenv

Maak een map aan waarin je de instellingen wil installeren:
mkdir venv
	virtualenv venv/v1 (of virtualviaduct of w/e)
Met
	virtualenv venv/v1 --no-site-packages
zorg je ervoor dat er geen packages die op je systeem geinstalleerd staan
gebruikt worden.

ga in je net gemaakt omgeving:
	source venv/v1/bin/activate
om er uit te gaan:
	deactivate

Als het goed is staat nu (v1) voor je prompt

Installeer yolk om handig te zien welke packages er gebruikt worden:
	pip install yolk
	yolk -l

Er komt zoiets uit:
yolk -l
Babel           - 0.9.6        - active development (/usr/local/lib/python2.7/dist-packages)
Flask-Babel     - 0.8          - active development (/usr/local/lib/python2.7/dist-packages)
Flask-Login     - 0.2.4        - active development (/usr/local/lib/python2.7/dist-packages)
Flask-RESTful   - 0.1.6        - active development (/usr/local/lib/python2.7/dist-packages)
Flask-SQLAlchemy - 0.16         - active development (/usr/local/lib/python2.7/dist-packages)
...
...

ssh naar de via server en kijk daar ook met yolk wat voor grappen daar allemaal
gebruikt worden.

ZORG DAT ZE GELIJK AAN ELKAAR ZIJN!

bijvoorbeeld:
	pip install flask-wtf==0.8.3

Ik hoop dat alles klopt, heb het niet weer allemaal nagelopen.
