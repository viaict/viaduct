from flask import render_template
from flask import Markup
from flask.ext.login import current_user

from application import application
from application.page.views import view_page

@application.route('/')
def index():
	return Markup(render_template('index.htm'))

def test():
	return 'testing'

def view_navigation_bar():
	return Markup(render_template('navigation/view_bar.htm'))

