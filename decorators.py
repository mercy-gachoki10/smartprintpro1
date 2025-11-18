from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def roles_required(*roles):
    """Ensure the current user matches one of the accepted roles."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(*args, **kwargs):
            if current_user.user_type not in roles:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator
