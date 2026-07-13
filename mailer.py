import socket
import smtplib

from flask import current_app
from flask_mail import Mail, Message

mail = Mail()


def mail_is_configured():
    return bool(current_app.config.get("MAIL_USERNAME") and current_app.config.get("MAIL_PASSWORD"))


def _try_send(msg):
    """Attempts to send an email. Returns True on success, False on ANY
    failure (not configured, DNS/network error, wrong credentials, etc.)
    so callers can always fall back to on-screen OTP display instead of
    crashing the request."""
    if not mail_is_configured():
        return False
    try:
        mail.send(msg)
        return True
    except (socket.gaierror, ConnectionError, smtplib.SMTPException, OSError) as e:
        # Network/DNS unreachable, wrong SMTP host/port, auth failure, etc.
        # Log it for debugging, but don't let it crash the request.
        current_app.logger.warning(f"OTP email failed to send, falling back to on-screen OTP: {e}")
        return False


def send_otp_email(to_email, name, otp_code):
    """Sends the sign-up OTP by email. Returns True if an email was actually
    sent, False if mail isn't configured OR sending failed for any reason
    (caller should fall back to on-screen display in that case)."""
    msg = Message(
        subject="Your Online Voting System OTP",
        recipients=[to_email],
        body=(
            f"Hi {name},\n\n"
            f"Your one-time verification code is: {otp_code}\n\n"
            f"Enter this code on the Verify OTP page to activate your account.\n"
            f"If you didn't request this, you can ignore this email.\n"
        ),
    )
    return _try_send(msg)


def send_password_reset_email(to_email, name, otp_code):
    """Sends a password-reset OTP by email. Same fallback behaviour as above."""
    msg = Message(
        subject="Reset your Online Voting System password",
        recipients=[to_email],
        body=(
            f"Hi {name},\n\n"
            f"Your password reset code is: {otp_code}\n\n"
            f"Enter this code on the Reset Password page to choose a new password.\n"
            f"If you didn't request this, you can safely ignore this email.\n"
        ),
    )
    return _try_send(msg)
