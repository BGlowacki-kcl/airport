from django.urls import path
from . import views

app_name = 'Users'

urlpatterns = [
    # All
    path('dashboard', views.dashboard, name='dashboard'),
    path('profile', views.profile, name='profile'),
    # Passenger
    path('pas/search-flights', views.search_flights, name='search-flights'),
    path('pas/my-tickets', views.my_tickets, name='my-tickets'),
    # Airport worker
    path('ap-w/task-manager', views.task_manager, name='task-manager'),
    path('ap-w/flight-schedule', views.flight_schedule, name='flight-schedule'),
    # Airport manager
    path('ap-m/flight-approval', views.flight_approval, name='flight-approval'),
    path('ap-m/task-assignment', views.task_assignment, name='task-assignment'),
    path('ap-m/workers', views.workers, name='workers'),
    # Airline manager
    path('al-m/flight-management', views.flight_management, name='flight-management'),
    path('al-m/passengers', views.passengers, name='passengers'),
    path('al-m/add-routes', views.add_routes, name='add-routes'),
    # Pilot
    path('pil/my-flights', views.my_flights, name='my-flights'),
    path('pil/flight-schedule-pilot', views.flight_schedule_pilot, name='flight-schedule-pilot'),
]