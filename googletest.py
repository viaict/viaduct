import viaduct.api.google as google
from pprint import pprint

service = google.build_groups_service()
pprint(dir(service))
groups_api = service.groups()

domain = 'via.uvastudent.org'

try:
    pprint(dir(groups_api))
    group = None
    """
    for g in groups_api.list(domain=domain).execute()['groups']:
        if g['email'] == 'ict@via.uvastudent.org':
            group = g

    pprint(groups_api.get(groupKey=group['id']).execute())
    """
    members_api = service.members()
    maillist = 'ict@' + domain
    pprint(members_api.list(groupKey=maillist).execute())
    members_api.delete(groupKey=maillist, memberKey='batman@bitchimfamo.us').execute()
    pprint(members_api.list(groupKey='ict@via.uvastudent.org').execute())
except Exception as e:
    print(e)
