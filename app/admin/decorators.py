from functools import wraps

from flask import abort
from flask_login import current_user


def system_admin_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if not current_user.is_authenticated:
            abort(401)

        if not current_user.is_system_admin:
            abort(403)

        if not current_user.is_active:
            abort(403)

        return view_function(
            *args,
            **kwargs
        )

    return wrapped_view