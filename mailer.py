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
        current_app.logger.warning("Mail is not configured.")
        return False

    try:
        with mail.connect() as conn:
            # Prevent long hangs
            conn.host.timeout = 10
            conn.send(msg)

        current_app.logger.info(
            f"OTP email sent successfully to {msg.recipients}"
        )
        return True

    except Exception as e:
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