from collections.abc import Callable
from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Требуется вход", "error")
            return redirect(url_for("auth.login"))

        if not getattr(current_user, "is_admin", False):
            flash("Требуется права администратора", "error")
            return redirect(url_for("chat.chat"))

        return func(*args, **kwargs)

    return wrapper
