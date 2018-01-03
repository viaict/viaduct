def search(group_id=None):
    return {"taskId": 69, "groupId": 4, "title": "Do shit", "status": "new"}


def post(task):
    print(task)


def get(task_id):
    print("task_id", task_id)
    return


def put(*args, **kwargs):
    print(kwargs)
    print(args)
    return
