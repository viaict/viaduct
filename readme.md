Install these modules:

 - flask
 - flask-login
 - flask-sqlalchemy
 - flask-wtf
 - MySQL-python
 - py-bcrypt
 - markdown


BUT HOW?
sudo apt-get install python-dev
sudo apt-get install libmysqlclient-dev
sudo apt-get install python-pip
sudo pip install flask flask-login flask-sqlalchemy flask-wtf
easy_install -U distribute
sudo pip install MySQL-python py-bcrypt markdown
sudo pip install flask-babel
sudo pip install flask-restful
sudo pip install validictory

VERVOLGENS (in root van de git repo):
ln -s local_config.py config.py
python create_db.py
python run.py

JEEEJ:
In de browser nu localhost:5000 checken
Echter, je db is nog super leeg
Als het niet werkt omdat ie modules mist, opnieuw pip install proberen!
