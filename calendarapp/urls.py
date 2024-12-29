from django.urls import path

from . import views

app_name = "calendarapp"


urlpatterns = [
    path("task/new/", views.TaskCreateView.as_view(), name="task_new"),
    path("task/<int:pk>/edit/", views.TaskUpdateView.as_view(), name="task_edit"),
    path("task/<int:pk>/delete/", views.TaskDeleteView.as_view(), name="task_delete"),
    path("calender/", views.CalendarViewNew.as_view(), name="calendar"),
    path("calenders/", views.CalendarView.as_view(), name="calendars"),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('modify_event/<int:event_id>/', views.modify_event, name='modify_event'),
    path('next_week/<int:event_id>/', views.next_week, name='next_week'),
    path('next_day/<int:event_id>/', views.next_day, name='next_day'),
    path("event/new/", views.create_event, name="event_new"),
    path("event/edit/<int:pk>/", views.EventEdit.as_view(), name="event_edit"),
    path("event/<int:event_id>/details/", views.event_details, name="event-detail"),
    path(
        "add_eventmember/<int:event_id>", views.add_eventmember, name="add_eventmember"
    ),
    path(
        "event/<int:pk>/remove",
        views.EventMemberDeleteView.as_view(),
        name="remove_event",
    ),
    path("all-event-list/", views.AllEventsListView.as_view(), name="all_events"),
    path(
        "running-event-list/",
        views.RunningEventsListView.as_view(),
        name="running_events",
    ),
    path(
        "upcoming-event-list/",
        views.UpcomingEventsListView.as_view(),
        name="upcoming_events",
    ),
    path(
        "completed-event-list/",
        views.CompletedEventsListView.as_view(),
        name="completed_events",
    ),
    path("all-task-list/", views.AllTasksListView.as_view(), name="all_tasks"),
    path("today-tasks-list/", views.TodayTasksListView.as_view(), name="today_tasks"),
    path("upcoming-tasks-list/", views.UpcomingTasksListView.as_view(), name="upcoming_tasks"),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('modify_task/<int:task_id>/', views.modify_task, name='modify_task'),
]
