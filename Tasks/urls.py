from django.urls import path
from . import views

app_name = 'Tasks'

urlpatterns = [
    # Approval
    path('ap-m/flight-to-approve/<str:flightId>', views.flight_to_approve, name='flight-to-approve'),
    # Assignment
    path('ap-m/flight-to-assign/<str:approvalId>', views.flight_to_assign, name='flight-to-assign'),
    # View worker
    path('ap-m/view-worker/<str:workerId>', views.view_worker, name='view-worker'),
    # Assign one task - report
    path('ap-m/change-one-assignment/<str:reportId>', views.change_one_assignment, name='change-one-assignment'),
    # Assign one task
    path('ap-m/change-one-assignment-normal/<str:taskId>', views.change_one_assignment_normal, name='change-one-assignment-normal'),
    # Send response
    path('ap-m/send-response/<str:reportId>', views.send_response, name='send-response'),
    # Task done
    path('ap-w/task-done/<str:taskId>', views.task_done, name='task-done'),
    # Report task
    path('ap-w/task-report/<str:taskId>', views.task_report, name='task-report'),
    # Report flight
    path('pil/report-flight', views.report_flight, name='report-flight'),
    # Report flight
    path('pil/report-flight-with-id/<str:flightId>', views.report_flight_with_id, name='report-flight-with-id'),
    # Contact other pilot
    path('pil/contact-pilot/<str:flightId>', views.contact_pilot, name='contact-pilot'),
]