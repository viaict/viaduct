from app import rest_api
from app.api.pimpy.minutes import MinuteResource, GroupMinuteResource
from app.api.pimpy.tasks import TaskListResource, TaskResource, \
    GroupTaskListResource

# Pimpy Tasks
rest_api.add_resource(TaskListResource,
                      '/api/tasks/',
                      endpoint="api.task")
rest_api.add_resource(TaskResource,
                      '/api/tasks/<string:task_id>',
                      endpoint="api.tasks")
rest_api.add_resource(GroupTaskListResource,
                      '/api/groups/<int:group_id>/tasks',
                      endpoint="api.groups.tasks")

# Pimpy Minutes
rest_api.add_resource(MinuteResource,
                      "/api/minutes/<int:minute_id>",
                      endpoint="api.minute")
rest_api.add_resource(GroupMinuteResource,
                      "/api/groups/<int:group_id>/minutes",
                      endpoint="api.groups.minutes")
