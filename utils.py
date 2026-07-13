import random
from functools import wraps
from flask import session, redirect, url_for, flash


def generate_otp():
    """Generates a 6-digit numeric OTP.

    NOTE: This is a demo/local implementation. In production, you would
    email or SMS this code to the user instead of showing it on screen —
    e.g. with Flask-Mail (email) or the Twilio API (SMS). Search for
    'TODO: send real OTP' in routes.py for where to plug that in.
    """
    return str(random.randint(100000, 999999))


def voter_login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if session.get("role") != "voter":
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


def admin_login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Please log in as an authorised admin to continue.", "error")
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)
    return wrapped
