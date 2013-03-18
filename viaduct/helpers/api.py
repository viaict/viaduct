def make_api_response(status_code, status):
	return {'status': status_code, 'message': status}, \
		'{0} {1}'.format(status_code, status)

