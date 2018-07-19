from app import api
from app.api.pimpy.minutes import MinuteResource, GroupMinuteResource
from app.api.pimpy.tasks import TaskListResource, TaskResource, \
    GroupTaskListResource

# Pimpy Tasks
api.add_resource(TaskListResource,
                 '/api/tasks/')
api.add_resource(TaskResource,
                 '/api/tasks/<string:task_id>')
api.add_resource(GroupTaskListResource,
                 '/api/groups/<int:group_id>/tasks')

# Pimpy Minutes
api.add_resource(MinuteResource,
                 "/api/minutes/<int:minute_id>")
api.add_resource(GroupMinuteResource,
                 "/api/groups/<int:group_id>/minutes")
