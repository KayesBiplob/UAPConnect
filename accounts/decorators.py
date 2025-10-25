from django.http import HttpRequest
from django.shortcuts import redirect


def redirect_autheticated_user(view_func):
    """Decorator to redirect authenticated users to home page"""
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return view_func(request, *args, **kwargs)
    
    return wrapper