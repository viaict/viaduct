from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from application.helpers import flash_form_errors

import os
from os import listdir
from os.path import isfile, join


tentamens_module = Blueprint('tentamens', __name__)

@tentamens_module.route('/tentamens/', methods = ['GET', 'POST'])
def view_tentamens():

	tentamens = ["help"]
	pathname = 'application/static/tentamens'
	tentamens = [ f for f in listdir(pathname) if isfile(join(pathname,f)) ]

	pathname = '../static/tentamens/'

	return render_template('tentamens/view.htm', pathname = pathname, tentamens = tentamens)

