from app import rest_api
from app.api.pimpy.minutes import MinuteResource, GroupMinuteResource
from app.api.pimpy.tasks import TaskListResource, TaskResource, \
    GroupTaskListResource

# Pimpy Tasks
rest_api.add_resource(TaskListResource,
                      '/api/tasks/')
rest_api.add_resource(TaskResource,
                      '/api/tasks/<string:task_id>')
rest_api.add_resource(GroupTaskListResource,
                      '/api/groups/<int:group_id>/tasks')

# Pimpy Minutes
rest_api.add_resource(MinuteResource,
                      "/api/minutes/<int:minute_id>")
rest_api.add_resource(GroupMinuteResource,
                      "/api/groups/<int:group_id>/minutes")
