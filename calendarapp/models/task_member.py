from django.db import models

from accounts.models import User
from calendarapp.models import Task, TaskAbstract


class TaskMember(TaskAbstract):
    """ Task member model """

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="tasks")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="task_members"
    )

    class Meta:
        unique_together = ["task", "user"]

    def __str__(self):
        return str(self.user)
