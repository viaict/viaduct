from flask import render_template, request

from viaduct.pimpy.models import Task, Minute

class PimpyAPI:
	def get_group_list(group id):
