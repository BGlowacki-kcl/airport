from django.contrib import admin
from .models import Approval, RegularTasks, Task, Report, PilotConversation, PilotMessage, FlightReport

admin.site.register(Approval)
admin.site.register(RegularTasks)
admin.site.register(Task)  
admin.site.register(Report)  
admin.site.register(FlightReport)
admin.site.register(PilotMessage)  
admin.site.register(PilotConversation)  