from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def login_required(view_func):
    """Decorador que requiere sesión iniciada."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorador que requiere rol de administrador."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, 'Debes iniciar sesión.')
            return redirect('login')
        if request.session.get('user_role') != 'admin':
            messages.error(request, 'No tienes permisos de administrador.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def artisan_required(view_func):
    """Decorador que requiere rol de artesano."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, 'Debes iniciar sesión.')
            return redirect('login')
        if request.session.get('user_role') != 'artisan':
            messages.error(request, 'No tienes permisos de artesano.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper
