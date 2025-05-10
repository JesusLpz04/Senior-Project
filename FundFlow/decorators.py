from django.http import HttpResponse
from django.shortcuts import redirect
from functools import wraps

def unauthorized_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return view_func(request, *args, **kwargs)
        
    return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper_func(request, *args, **kwargs):
            # First check if user is authenticated
            if not request.user.is_authenticated:
                return HttpResponse('You need to be logged in to access this page.')
            
            # Check if the user has a profile
            try:
                # Access the user profile through the one-to-one relationship
                user_type = request.user.userprofile.user_type
                
                if user_type in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponse('You are trying to access an unauthorized page.')
            except:
                # If no UserProfile exists or there's another error
                return HttpResponse('User profile not found or other error occurred.')
                
        return wrapper_func
    return decorator