from django.shortcuts import redirect

class AuthRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path != '/auth/user-logout':
            if request.path.startswith('/auth/') and request.user.is_authenticated:
                return redirect('Users:dashboard')
        response = self.get_response(request)
        return response