from flask import current_app
from flask_mail import Mail, Message

mail = Mail()


def mail_is_configured():
    return bool(
        current_app.config.get("MAIL_USERNAME")
        and current_app.config.get("MAIL_PASSWORD")
    )


def _try_send(msg):
    if not mail_is_configured():
        current_app.logger.warning(
            "Mail is not configured (missing MAIL_USERNAME or MAIL_PASSWORD)."
        )
        return False

    missing = []
    if not current_app.config.get("MAIL_DEFAULT_SENDER"):
        missing.append("MAIL_DEFAULT_SENDER")
    if not current_app.config.get("MAIL_SERVER"):
        missing.append("MAIL_SERVER")

    if missing:
        current_app.logger.warning(f"Mail config missing keys: {', '.join(missing)}")

    try:
        with mail.connect() as conn:
            # Keep timeouts reasonable for web onboarding.
            if hasattr(conn, "host") and hasattr(conn.host, "timeout"):
                conn.host.timeout = current_app.config.get("MAIL_TIMEOUT", 10)

            conn.send(msg)

        current_app.logger.info("Email sent successfully.")
        return True
    except Exception as e:
        current_app.logger.exception(e)
        current_app.logger.error(f"Failed to send OTP email: {str(e)}")
        return False





def send_otp_email(to_email, name, otp_code):
    msg = Message(
        subject="Your Online Voting System OTP",
        recipients=[to_email],
        body=(
            f"Hi {name},\n\n"
            f"Your One-Time Password (OTP) is: {otp_code}\n\n"
            f"This OTP is valid for verification only.\n\n"
            f"If you did not request this, please ignore this email.\n\n"
            f"Thank you."
        ),
    )
    return _try_send(msg)


def send_password_reset_email(to_email, name, otp_code):
    msg = Message(
        subject="Reset Your Online Voting System Password",
        recipients=[to_email],
        body=(
            f"Hi {name},\n\n"
            f"Your password reset OTP is: {otp_code}\n\n"
            f"If you did not request this, please ignore this email."
        ),
    )
    return _try_send(msg)