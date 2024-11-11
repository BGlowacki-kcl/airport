from django.contrib import admin
from .models import Airport, Airline, WorksForAirline, WorksForAirport, Plane, Fleet, CanFlyTo, CanFlyFrom, Flight, Ticket

admin.site.register(Airport)
admin.site.register(Airline)
admin.site.register(Plane)
admin.site.register(Fleet)
admin.site.register(CanFlyTo)
admin.site.register(Flight)
admin.site.register(Ticket)
admin.site.register(WorksForAirline)
admin.site.register(WorksForAirport)
admin.site.register(CanFlyFrom)