from django.urls import path

from . import views
from .views.other_views import ExternalServicesView 

app_name = "calendarapp"


urlpatterns = [
    path('external-services/', ExternalServicesView.as_view(), name='external_services'),
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
    path("all-event-list/", views.AllEventsListView.as_view(), name="all_events"),
    path(
        "today-event-list/",
        views.TodayEventsListView.as_view(),
        name="today_events",
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
    path('process-edusoft/', views.process_edusoft, name='process_edusoft'),
    path('process-blackboard/', views.process_blackboard, name='process_blackboard'),
]
