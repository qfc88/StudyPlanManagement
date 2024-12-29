from django.views.generic import ListView

from calendarapp.models import Task


class AllTasksListView(ListView):
    """ All task list views """

    template_name = "calendarapp/tasks_list.html"
    model = Task

    def get_queryset(self):
        return Task.objects.get_all_tasks(user=self.request.user)


class TodayTasksListView(ListView):
    """ Running tasks list view """

    template_name = "calendarapp/tasks_list.html"
    model = Task

    def get_queryset(self):
        return Task.objects.get_today_tasks(user=self.request.user)

class UpcomingTasksListView(ListView):
    """ Upcoming tasks list view """

    template_name = "calendarapp/tasks_list.html"
    model = Task

    def get_queryset(self):
        return Task.objects.get_upcoming_tasks(user=self.request.user)
    
class IncompletedTasksListView(ListView):
    """ Incompleted tasks list view """

    template_name = "calendarapp/tasks_list.html"
    model = Task

    def get_queryset(self):
        return Task.objects.get_incompleted_tasks(user=self.request.user)
    

def get_view_name(self):
    """Return view name for the template"""
    if self.__class__ == AllTasksListView:
        return "All Tasks"
    elif self.__class__ == TodayTasksListView:
        return "Today's Tasks"
    elif self.__class__ == UpcomingTasksListView:
        return "Upcoming Tasks"
    elif self.__class__ == IncompletedTasksListView:
        return "Incompleted Tasks"
    return "Tasks"
