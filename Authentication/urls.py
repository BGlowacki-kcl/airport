from django.urls import path
from . import views

app_name = 'Authentication'

urlpatterns = [
    path('', views.home, name=""),
    path('login', views.login, name="login"),
    path('register', views.register, name="register"),
    path('about', views.about, name="about"),
    path('user-logout', views.user_logout, name="user-logout"),
]