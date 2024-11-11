from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
#from Authentication.views import handler404

urlpatterns = [
    path('', lambda request: redirect('auth/')),

    path("admin/", admin.site.urls),
    path('auth/', include('Authentication.urls')),
    path('users/', include('Users.urls')),
    path('database/', include('Database.urls')),
    path('tasks/', include('Tasks.urls')),
]

#handler404 = 'Authentication.views.handler404'

# 0. live chat for passenger with airline manager
# 2. Answer to reports from pilots by airline manager
# 3. See tasks button in flight schedule in airport worker
# 4. Profile and dashboard for users
# x. Notifications
# y. Setting managers by email
# z. contracting workers and pilots
# q. adding favicons
# w. adding planes to fleet
# 6. sticky navbar everywhere
# 7. ML model for price 
# 8. recommendation system