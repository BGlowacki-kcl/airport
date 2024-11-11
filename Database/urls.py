from django.urls import path
from . import views

app_name = 'Database'

urlpatterns = [
    # Passenger
    path('pas/one-flight-pas/<str:flightId>', views.one_flight_pas, name='one-flight-pas'),
    path('pas/pay-page', views.pay_page, name='pay-page'), 
    path('pas/pay-page/transaction-succesfull', views.transaction_succesfull, name='transaction-succesfull'),
    path('pas/pay-page/transaction-unsuccesfull', views.transaction_unsuccesfull, name="transaction-unsuccesfull"),
    path('pas/enter-amount', views.process_payment_form ,name='process_payment_form'),
    path('pas/delete-ticket/<str:ticketId>', views.delete_ticket, name='delete-ticket'),
    path('pas/deleted-ticket', views.deleted_ticket, name='deleted-ticket'),
    path('pas/choose-seat', views.choose_seat, name='choose-seat'),
    path('pas/save-seat-to-session/', views.save_seat_to_session, name='save-seat-to-session'),
    # Airline manager
    path('al-m/delete-flight-man', views.delete_flight_man, name='delete-flight-man'),
    path('al-m/create-flight', views.create_flight, name='create-flight'),
    path('al-m/one-flight-man/<str:flightId>', views.one_flight_man, name='one-flight-man'),
    path('al-m/one-passenger-man/<str:username>', views.one_pas_man, name='one-passenger-man'),
    path('al-m/man-edit-pas/<str:ticketId>', views.man_edit_pas, name='man-edit-pas'),
    path('al-m/man-delete-pas/<str:ticketId>', views.man_delete_pas, name='man-delete-pas'),
    path('al-m/reschedule-man/<str:flightNumber>', views.reschedule_man, name='reschedule-man'),
    # Pilot
    path('pil/flight-details/<str:flightId>', views.flight_details, name='flight-details'),
    path('pil/change-flight-status/<str:flightId>', views.change_flight_status, name='change-flight-status'),
]