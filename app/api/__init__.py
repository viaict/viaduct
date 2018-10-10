from app import rest_api
from app.api.group.users import GroupUserListResource
from app.api.pimpy.minutes import MinuteResource, GroupMinuteResource
from app.api.pimpy.tasks import TaskListResource, TaskResource, \
    GroupTaskListResource
from app.api.user.address import UserAddressResource
from app.api.user.avatar import UserAvatarResource
from app.api.user.membership import UserMembershipResource
from app.api.user.user import UserResource, UserListResource

# Pimpy Tasks
rest_api.add_resource(TaskListResource,
                      "/tasks/",
                      endpoint="api.task")
rest_api.add_resource(TaskResource,
                      "/tasks/<string:task_id>/",
                      endpoint="api.tasks")
rest_api.add_resource(GroupTaskListResource,
                      "/groups/<int:group_id>/tasks/",
                      endpoint="api.groups.tasks")

# Pimpy Minutes
rest_api.add_resource(MinuteResource,
                      "/minutes/<int:minute_id>/",
                      endpoint="api.minute")
rest_api.add_resource(GroupMinuteResource,
                      "/groups/<int:group_id>/minutes/",
                      endpoint="api.groups.minutes")

# User
rest_api.add_resource(UserListResource,
                      "/users/",
                      endpoint="api.user")
rest_api.add_resource(UserResource,
                      "/users/<int:user_id>/",
                      endpoint="api.users")
rest_api.add_resource(GroupUserListResource,
                      "/groups/<int:group_id>/users/",
                      endpoint="api.groups.users")

# TODO discuss routes, maybe put in single nested response.
rest_api.add_resource(UserAddressResource,
                      "/users/<int:user_id>/address")
rest_api.add_resource(UserMembershipResource,
                      "/users/<int:user_id>/membership")
rest_api.add_resource(UserAvatarResource,
                      "/users/<int:user_id>/avatar")
