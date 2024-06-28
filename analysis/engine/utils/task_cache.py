"""
Used to create tasks for optimizer.
"""


class TasksCache:
    """used to create tasks for optimizer"""
    tasks = {}

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(TasksCache, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    @classmethod
    def get_instance(cls):
        """get instance"""
        if cls.__instance is None:
            cls.__instance = TasksCache()
        return cls.__instance

    def get(self, key):
        """get task according to key"""
        return self.tasks.get(key) if key in self.tasks.keys() else None

    def set(self, key, value):
        """set task according to key"""
        self.tasks[key] = value

    def delete(self, key):
        """delete task according to key"""
        del self.tasks[key]

    def get_all(self):
        """get all task"""
        return self.tasks