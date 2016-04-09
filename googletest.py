import app.api.google as google
from pprint import pprint




service = google.build_groups_service()
groups_api = service.groups()
pprint(google.create_group('ICT testmail list', 'icttest'))
