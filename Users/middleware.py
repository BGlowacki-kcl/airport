from django.shortcuts import redirect, render
from Database.models import Flight, Airline
from django.shortcuts import get_object_or_404

class UserRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (request.path.startswith('/users/') or request.path.startswith('/database/') or request.path.startswith('/tasks/')) and not request.user.is_authenticated:
            return redirect('Authentication:login')
        response = self.get_response(request)
        return response

class UserAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/":
            if not request.user.is_authenticated:
                return redirect("Authentication:")
            else:
                return redirect("Users:dashboard")
        if request.path.startswith('/admin/'):
            return self.get_response(request)
        if request.path != '/auth/user-logout':
            prefixes = {'passenger': 'pas', 'airport_worker': 'ap-w', 'airport_manager': 'ap-m', 'airline_manager': 'al-m', 'pilot': 'pil'}
            if request.user.is_authenticated:
                if request.user.role is not None:
                    roleName = request.user.role.name
                    print(roleName)
                    if prefixes.get(roleName) not in request.path.split('/') and not request.path.endswith('/dashboard') and not request.path.endswith('/profile'):
                        print('--------------------', request.path)
                        return render(request, "Users/restricted-access.html") #HttpResponseForbidden("You don't have permission to access this page.")
        return self.get_response(request)
 