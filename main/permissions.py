from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def is_editor(user):
    """The Editor group is managed by the portfolio owner in Django Admin."""
    return user.is_authenticated and user.groups.filter(name="Editor").exists()


def portfolio_permission_required(*, allow_editor=False):
    """Redirect guests to login and reject authenticated users without access."""
    def decorator(view):
        @login_required(login_url="main:login")
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            allowed = request.user.is_superuser or (
                allow_editor and is_editor(request.user)
            )
            if not allowed:
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapped

    return decorator
