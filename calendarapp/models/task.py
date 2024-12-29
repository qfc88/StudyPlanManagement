from datetime import datetime
from django.db import models
from django.urls import reverse


from accounts.models import User
from calendarapp.models import TaskAbstract


class TaskManager(models.Manager):
    """ Task manager """

    def get_all_tasks(self, user):
        tasks = Task.objects.filter(user=user, is_active=True, is_deleted=False)
        return tasks

    def get_today_tasks(self, user):
        today = datetime.now().date()
        today_tasks = Task.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False,
            deadline__date=today
        ).order_by('deadline')
        return today_tasks
    
    
    def get_upcoming_tasks(self, user):
        upcoming_tasks = Task.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False,
            deadline__gt=datetime.now()  # Changed to get tasks with deadline in future
        ).order_by('deadline')  # Order by deadline
        return upcoming_tasks


class Task(TaskAbstract):
    """ Task model """
    is_completed = models.BooleanField(default=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()


    objects = TaskManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("calendarapp:task-detail", args=(self.id,))

    @property
    def get_html_url(self):
        url = reverse("calendarapp:task-detail", args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'
