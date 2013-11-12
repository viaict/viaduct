from viaduct import db

from sqlalchemy import or_

#from viaduct.models.* import *


class SearchAPI:
	"""
	This module can be used to search through the database.

	A user should supply two things: the query as string,
	and a dictionairy with table names as keys, and a list of
	table columns as values. This dictionairy indicates which
	part of the database is to be search.

	The query will be split on spaces (' '), allowing any of
	the query's words to match on any part of the given part of
	the database.
	"""

	#@staticmethod
	#def search_BAD(query, part):
	#	"""Searches a part of the database for the query.

	#	query is a string containing the query.
	#	part is a dictionairy containing the part of the database
	#	to be searched.

	#	See API documentation for specifics.
	#	"""
	#	query_splitted = query.split()

	#	final_result = []

	#	# this is to be optimized later, but for now a proof
	#	# of concept will do fine!
	#	for db_model in part.keys():
	#		columns = part[db_model]
	#		for column in columns:
	#			if column not in vars(db_model).keys():
	#				raise Exception("Model %s does not contain %s as column" % \
	#					(db_model, column))
	#			for query_element in query_splitted:
	#				column_element = vars(db_element)[column]
	#				query = db_element.query.filter(
	#					column_element.like('%%%s%%' % query_element))
	#				final_result.extend(query.all())

	@staticmethod
	def search(stack, needle, case_insensitive=True):
		"""Generic search on specified database tables and columns.

		Parameters:
		* stack is a list of (table, [columns]) tuples.
		* needle is a string which will be split for seperate words.
		* case_insensitive a boolean indicating case sensitive or insensitive
			search, default is True

		Returns:
			A set of db.models that have matched the queries

		Example:
			> stack = [ (Examination, [Examination.title]),
				(Course, [Course.name]),
				(Education, [Education.name])]
			> needle = "inf"
			> print searchAPI.search(stack, needle)
			set([<viaduct.models.education.Education object at 0x7f4f5c2ac650>, <viaduct.models.education.Education object at 0x7f4f5c2ac710>])
			# (this should contain Informatica and Informatiekunde)
		"""
		result_list = []

		for model, columns in stack:
			for word in ["%%%s%%" % word for word in needle.split()]:
				result_list.extend(model.query.filter(*[column.ilike(word) \
					if case_insensitive else column.like(word) for column in \
					columns]).all())

		return set(result_list)


	#@staticmethod
	#def search(stack, needle, case_insensitive=True):
	#	# stackle = list of tuples:
	#	# tuple[0]= db.Model objects. tuple[1]= db.Column objects

	#	query_splitted = needle.split()
	#	query_list = []

	#	# join the tables we want to search
	#	query = stack[0][0].query
	#	for model in [pair[0] for pair in stack[1:]]:
	#		query = query.join(model)

	#	# built a list of 'like' query elements
	#	for model, column_list in stack:
	#		for column in column_list:
	#			for query_element in query_splitted:
	#				print "%%%s%%" % query_element
	#				query_list.append(column.ilike('%%%s%%' % query_element) \
	#					if case_insensitive else \
	#					column.like('%%%s%%' % query_element))

	#	# execute query
	#	query = query.filter(or_(*query_list))
	#	print query

	#	# combinin' both, and return
	#	#return query.filter(or_(*query_list)).all()
	#	return query.all()

