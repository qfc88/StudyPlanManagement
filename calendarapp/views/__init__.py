from .event_list import AllEventsListView, CompletedEventsListView, RunningEventsListView, UpcomingEventsListView
from .task_list import AllTasksListView, TodayTasksListView, UpcomingTasksListView, IncompletedTasksListView
from .task_views import TaskCreateView, TaskUpdateView, TaskDeleteView
from .task_views import delete_task, modify_task
from .other_views import (
    CalendarViewNew,
    CalendarView,
    create_event,
    EventEdit,
    event_details,
    delete_event,
    next_week,
    next_day,
    modify_event,
    ExternalServicesView,
    process_edusoft,     
    process_blackboard,
)


__all__ = [
    AllEventsListView,
    RunningEventsListView,
    UpcomingEventsListView,
    CompletedEventsListView,
    CalendarViewNew,
    CalendarView,
    create_event,
    EventEdit,
    event_details,
    delete_event,
    next_week,
    next_day,
    modify_event,
    TaskCreateView,
    TaskUpdateView,
    TaskDeleteView,
    AllTasksListView,
    TodayTasksListView,
    UpcomingTasksListView,
    delete_task,
    modify_task,
    ExternalServicesView,
    process_edusoft,     
    process_blackboard,
]
