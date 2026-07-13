from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class Admin(db.Model):
    """Election officer / admin account. Completely separate from voters."""
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class User(db.Model):
    """A voter account. Must be OTP-verified AND admin-approved before voting."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    pin = db.Column(db.String(20), unique=True, nullable=False)      # login identifier
    password_hash = db.Column(db.String(255), nullable=False)

    # OTP verification (first sign-in only)
    otp_code = db.Column(db.String(6))
    otp_verified = db.Column(db.Boolean, default=False)

    # Forgot-password OTP (separate from the sign-up OTP above)
    reset_otp_code = db.Column(db.String(6))

    # Admin approval workflow: pending -> approved / rejected
    status = db.Column(db.String(20), default="pending")  # pending | approved | rejected
    rejection_reason = db.Column(db.String(255))

    # Voting
    has_voted = db.Column(db.Boolean, default=False)
    voted_for_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notifications = db.relationship("Notification", backref="user", lazy=True,
                                     order_by="Notification.created_at.desc()")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class Candidate(db.Model):
    """A candidate registered by the admin — Leader or CR position."""
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    symbol = db.Column(db.String(60), nullable=False)
    position = db.Column(db.String(30), nullable=False, default="Leader")  # 'Leader' or 'CR'
    votes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ElectionConfig(db.Model):
    """A single row holding the admin-declared voting window."""
    __tablename__ = "election_config"

    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, nullable=True)
    end_datetime = db.Column(db.DateTime, nullable=True)

    @staticmethod
    def get_or_create():
        cfg = ElectionConfig.query.first()
        if not cfg:
            cfg = ElectionConfig()
            db.session.add(cfg)
            db.session.commit()
        return cfg

    def status(self):
        if not self.start_datetime or not self.end_datetime:
            return "unset"
        # Uses local server time (not UTC) because the admin enters the
        # schedule using their own local clock via the datetime-local input.
        now = datetime.now()
        if now < self.start_datetime:
            return "upcoming"
        if now > self.end_datetime:
            return "closed"
        return "open"


class Notification(db.Model):
    """In-app notification sent to a user (e.g. approval/rejection)."""
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    kind = db.Column(db.String(20), default="info")  # info | success | error
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
