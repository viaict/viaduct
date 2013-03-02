from flask import render_template
from flask import Markup
from flask.ext.login import current_user

from application import application
from application.page.views import retrieve_page

@application.route('/')
def index():
	blocks = [ retrieve_page("index/" + str(i)) for i in range(1, 5) ]

	return render_template('index.htm', blocks = blocks)

def test():
	return 'testing'

def view_navigation_bar():
	return Markup(render_template('navigation/view_bar.htm'))

