import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash

from config import Config
from extensions import db
from models import Admin, User, Candidate, ElectionConfig, Notification
from utils import generate_otp, voter_login_required, admin_login_required
from mailer import mail, send_otp_email, send_password_reset_email
from dotenv import load_dotenv
load_dotenv()
print("MAIL_USERNAME:",os.environ.get("MAIL_USERNAME"))
print("MAIL_PASSWORD:",os.environ.get("MAIL_PASSWORD"))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.join(Config.BASE_DIR, "instance"), exist_ok=True)

    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        db.create_all()
        _seed_admin(app)

    register_routes(app)
    return app


def _seed_admin(app):
    """Creates the default admin account the first time the app runs."""
    if Admin.query.count() == 0:
        admin = Admin(username=app.config["DEFAULT_ADMIN_USERNAME"])
        admin.set_password(app.config["DEFAULT_ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()
        print(
            f"[setup] Created default admin -> "
            f"username: {app.config['DEFAULT_ADMIN_USERNAME']}  "
            f"password: {app.config['DEFAULT_ADMIN_PASSWORD']}"
        )


def register_routes(app):

    # ---------------------------------------------------------------
    # Makes the election schedule available on every page (for the
    # scrolling ticker banner), without needing to pass it in each route.
    # ---------------------------------------------------------------
    @app.context_processor
    def inject_election_schedule():
        cfg = ElectionConfig.get_or_create()
        return dict(ticker_cfg=cfg, ticker_status=cfg.status())

    # ---------------------------------------------------------------
    # HOME
    # ---------------------------------------------------------------
    @app.route("/")
    def home():
        return render_template("home.html")

    # ---------------------------------------------------------------
    # VOTER: SIGN UP  ->  OTP VERIFY  ->  (pending admin approval)
    # ---------------------------------------------------------------
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            pin = request.form.get("pin", "").strip()
            password = request.form.get("password", "").strip()

            if not name or not email or not pin or not password:
                flash("Please fill in all fields.", "error")
                return render_template("signup.html")

            if User.query.filter_by(pin=pin).first():
                flash("That PIN is already registered. Please choose another.", "error")
                return render_template("signup.html")

            if User.query.filter_by(email=email).first():
                flash("An account with that email already exists.", "error")
                return render_template("signup.html")

            user = User(name=name, email=email, pin=pin, status="pending")
            user.set_password(password)
            user.otp_code = generate_otp()
            user.otp_verified = False
            db.session.add(user)
            db.session.commit()

            sent = send_otp_email(user.email, user.name, user.otp_code)
            app.logger.info(f"OTP={user.otp_code}")
            app.logger.info(f"Email sent? {sent}")         
            if sent:
                flash(f"✅ OTP emailed to {user.email}. Check your inbox and enter the code below.", "success")
                session["otp_sent_by_email"] = True
            else:
                # Email not configured or blocked — store OTP in session
                # so it can be displayed prominently on the verify page.
                session["demo_otp"] = user.otp_code
                session["otp_sent_by_email"] = False
                flash("OTP generated! Check the code shown below.", "info")

            session["pending_pin"] = pin
            return redirect(url_for("verify_otp"))

        return render_template("signup.html")

    @app.route("/verify-otp", methods=["GET", "POST"])
    def verify_otp():
        pin = session.get("pending_pin", "")

        if request.method == "POST":
            pin = request.form.get("pin", "").strip()
            code = request.form.get("otp", "").strip()
            user = User.query.filter_by(pin=pin).first()

            if not user:
                flash("No account found with that PIN.", "error")
                return render_template("verify_otp.html", pin=pin, demo_otp=session.get("demo_otp"), email_sent=session.get("otp_sent_by_email", False))

            if user.otp_verified:
                flash("This account is already verified. Please log in.", "info")
                return redirect(url_for("login"))

            if code != user.otp_code:
                flash("Incorrect OTP. Please try again.", "error")
                return render_template("verify_otp.html", pin=pin, demo_otp=session.get("demo_otp"), email_sent=session.get("otp_sent_by_email", False))

            user.otp_verified = True
            db.session.commit()
            session.pop("pending_pin", None)
            flash("Your account is verified! It is now pending admin approval before you can vote.", "success")
            return redirect(url_for("login"))

        return render_template("verify_otp.html", pin=pin, demo_otp=session.get("demo_otp"), email_sent=session.get("otp_sent_by_email", False))

    @app.route("/resend-otp/<pin>")
    def resend_otp(pin):
        user = User.query.filter_by(pin=pin).first()
        if user and not user.otp_verified:
            user.otp_code = generate_otp()
            db.session.commit()
            sent = send_otp_email(user.email, user.name, user.otp_code)
            if sent:
                flash(f"✅ A new OTP has been emailed to {user.email}.", "success")
                session["otp_sent_by_email"] = True
                session.pop("demo_otp", None)
            else:
                session["demo_otp"] = user.otp_code
                session["otp_sent_by_email"] = False
                flash("New OTP generated! Check the code shown below.", "info")
        return redirect(url_for("verify_otp"))

    # ---------------------------------------------------------------
    # VOTER: LOGIN / LOGOUT
    # ---------------------------------------------------------------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            pin = request.form.get("pin", "").strip()
            password = request.form.get("password", "").strip()
            user = User.query.filter_by(pin=pin).first()

            if not user or not user.check_password(password):
                flash("Invalid PIN or password.", "error")
                return render_template("login.html")

            if not user.otp_verified:
                session["pending_pin"] = pin
                flash("Please verify the OTP sent on your first sign-in before logging in.", "info")
                return redirect(url_for("verify_otp"))

            session["role"] = "voter"
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"))

    # ---------------------------------------------------------------
    # VOTER: FORGOT PASSWORD / RESET PASSWORD
    # ---------------------------------------------------------------
    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            identifier = request.form.get("identifier", "").strip()
            user = User.query.filter(
                (User.email == identifier.lower()) | (User.pin == identifier)
            ).first()

            # Always show the same message, whether or not an account exists —
            # this avoids leaking which PINs/emails are registered.
            generic_msg = "If that account exists, a reset code has been sent."

            if user:
                user.reset_otp_code = generate_otp()
                db.session.commit()
                sent = send_password_reset_email(user.email, user.name, user.reset_otp_code)
                if sent:
                    flash(generic_msg, "success")
                else:
                    flash(f"Demo mode (email not configured): your reset code is {user.reset_otp_code}.", "info")
                session["reset_pin"] = user.pin
            else:
                flash(generic_msg, "success")

            return redirect(url_for("reset_password"))

        return render_template("forgot_password.html")

    @app.route("/reset-password", methods=["GET", "POST"])
    def reset_password():
        pin = session.get("reset_pin", "")

        if request.method == "POST":
            pin = request.form.get("pin", "").strip()
            code = request.form.get("otp", "").strip()
            new_password = request.form.get("password", "").strip()
            user = User.query.filter_by(pin=pin).first()

            if not user or not user.reset_otp_code or code != user.reset_otp_code:
                flash("Invalid PIN or reset code.", "error")
                return render_template("reset_password.html", pin=pin)

            if len(new_password) < 4:
                flash("Please choose a password at least 4 characters long.", "error")
                return render_template("reset_password.html", pin=pin)

            user.set_password(new_password)
            user.reset_otp_code = None
            db.session.commit()
            session.pop("reset_pin", None)
            flash("Your password has been reset. Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("reset_password.html", pin=pin)

    # ---------------------------------------------------------------
    # VOTER: DASHBOARD (status + notifications) / VOTE / THANK YOU
    # ---------------------------------------------------------------
    @app.route("/dashboard")
    @voter_login_required
    def dashboard():
        user = User.query.get(session["user_id"])
        cfg = ElectionConfig.get_or_create()
        notifications = user.notifications[:5]
        return render_template(
            "dashboard.html", user=user, election_status=cfg.status(), notifications=notifications
        )

    @app.route("/notifications/mark-read")
    @voter_login_required
    def mark_notifications_read():
        Notification.query.filter_by(user_id=session["user_id"], is_read=False).update({"is_read": True})
        db.session.commit()
        return redirect(url_for("dashboard"))

    @app.route("/vote", methods=["GET", "POST"])
    @voter_login_required
    def vote():
        user = User.query.get(session["user_id"])
        cfg = ElectionConfig.get_or_create()
        status = cfg.status()

        if user.status != "approved":
            flash("Only admin-approved voters may access the ballot.", "error")
            return redirect(url_for("dashboard"))

        if user.has_voted:
            return redirect(url_for("thank_you"))

        candidates = Candidate.query.order_by(Candidate.position, Candidate.name).all()

        if request.method == "POST":
            if status != "open":
                flash("Voting is not currently open.", "error")
                return redirect(url_for("dashboard"))

            candidate_id = request.form.get("candidate_id")
            candidate = Candidate.query.get(candidate_id) if candidate_id else None
            if not candidate:
                flash("Please select a candidate before submitting.", "error")
                return render_template("vote.html", candidates=candidates, status=status)

            user.has_voted = True
            user.voted_for_id = candidate.id
            candidate.votes += 1
            db.session.commit()
            return redirect(url_for("thank_you"))

        return render_template("vote.html", candidates=candidates, status=status)

    @app.route("/thank-you")
    @voter_login_required
    def thank_you():
        user = User.query.get(session["user_id"])
        if not user.has_voted:
            return redirect(url_for("dashboard"))
        return render_template("thank_you.html", user=user)

    # ---------------------------------------------------------------
    # RESULTS (public)
    # ---------------------------------------------------------------
    @app.route("/results")
    def results():
        cfg = ElectionConfig.get_or_create()
        candidates = Candidate.query.order_by(Candidate.votes.desc()).all()
        total_voters = User.query.filter_by(status="approved").count()
        total_voted = User.query.filter_by(status="approved", has_voted=True).count()
        total_votes_cast = sum(c.votes for c in candidates)
        max_votes = max([c.votes for c in candidates], default=0)
        winners = [c for c in candidates if c.votes == max_votes and max_votes > 0]

        return render_template(
            "results.html",
            candidates=candidates,
            total_voters=total_voters,
            total_voted=total_voted,
            total_votes_cast=total_votes_cast,
            winners=winners,
            max_votes=max_votes,
            status=cfg.status(),
        )

    # ---------------------------------------------------------------
    # ADMIN: LOGIN / LOGOUT
    # ---------------------------------------------------------------
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()
            admin = Admin.query.filter_by(username=username).first()

            if not admin or not admin.check_password(password):
                flash("Invalid admin credentials.", "error")
                return render_template("admin_login.html")

            session["role"] = "admin"
            session["admin_id"] = admin.id
            return redirect(url_for("admin_dashboard"))

        return render_template("admin_login.html")

    # ---------------------------------------------------------------
    # ADMIN: DASHBOARD / OVERVIEW
    # ---------------------------------------------------------------
    @app.route("/admin/dashboard")
    @admin_login_required
    def admin_dashboard():
        pending_count = User.query.filter_by(status="pending", otp_verified=True).count()
        approved_count = User.query.filter_by(status="approved").count()
        rejected_count = User.query.filter_by(status="rejected").count()
        candidate_count = Candidate.query.count()
        cfg = ElectionConfig.get_or_create()
        return render_template(
            "admin_dashboard.html",
            pending_count=pending_count,
            approved_count=approved_count,
            rejected_count=rejected_count,
            candidate_count=candidate_count,
            election_status=cfg.status(),
        )

    # ---------------------------------------------------------------
    # ADMIN: MANAGE VOTER REQUESTS (accept / reject)
    # ---------------------------------------------------------------
    @app.route("/admin/users")
    @admin_login_required
    def admin_users():
        pending = User.query.filter_by(status="pending", otp_verified=True).order_by(User.created_at).all()
        approved = User.query.filter_by(status="approved").order_by(User.created_at).all()
        rejected = User.query.filter_by(status="rejected").order_by(User.created_at).all()
        return render_template("admin_users.html", pending=pending, approved=approved, rejected=rejected)

    @app.route("/admin/users/<int:user_id>/accept", methods=["POST"])
    @admin_login_required
    def accept_user(user_id):
        user = User.query.get_or_404(user_id)
        user.status = "approved"

        approval_msg = "Great news! Your registration has been approved. You can now cast your vote once polls open."
        cfg = ElectionConfig.get_or_create()
        if cfg.start_datetime and cfg.end_datetime:
            approval_msg += (
                f" Voting is scheduled from {cfg.start_datetime.strftime('%B %d, %Y at %I:%M %p')} "
                f"to {cfg.end_datetime.strftime('%B %d, %Y at %I:%M %p')}."
            )

        db.session.add(Notification(user_id=user.id, message=approval_msg, kind="success"))
        db.session.commit()
        flash(f"{user.name} has been approved to vote.", "success")
        return redirect(url_for("admin_users"))

    @app.route("/admin/users/<int:user_id>/reject", methods=["POST"])
    @admin_login_required
    def reject_user(user_id):
        user = User.query.get_or_404(user_id)
        reason = request.form.get("reason", "").strip()
        user.status = "rejected"
        user.rejection_reason = reason or "No reason provided."
        db.session.add(Notification(
            user_id=user.id,
            message=f"Your registration request was rejected. Reason: {user.rejection_reason}",
            kind="error",
        ))
        db.session.commit()
        flash(f"{user.name}'s request has been rejected.", "info")
        return redirect(url_for("admin_users"))

    # ---------------------------------------------------------------
    # ADMIN: REGISTER CANDIDATES (Leaders / CRs — separate sections)
    # ---------------------------------------------------------------
    @app.route("/admin/candidates", methods=["GET", "POST"])
    @admin_login_required
    def admin_candidates():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            symbol = request.form.get("symbol", "").strip()
            position = request.form.get("position", "Leader").strip()

            if not name or not symbol:
                flash("Candidate name and symbol are required.", "error")
            else:
                db.session.add(Candidate(name=name, symbol=symbol, position=position))
                db.session.commit()
                flash(f"{name} registered as {position} candidate.", "success")
            return redirect(url_for("admin_candidates"))

        leaders = Candidate.query.filter_by(position="Leader").order_by(Candidate.name).all()
        crs = Candidate.query.filter_by(position="CR").order_by(Candidate.name).all()
        return render_template("admin_candidates.html", leaders=leaders, crs=crs)

    @app.route("/admin/candidates/<int:candidate_id>/delete", methods=["POST"])
    @admin_login_required
    def delete_candidate(candidate_id):
        candidate = Candidate.query.get_or_404(candidate_id)
        db.session.delete(candidate)
        db.session.commit()
        flash("Candidate removed.", "info")
        return redirect(url_for("admin_candidates"))

    # ---------------------------------------------------------------
    # ADMIN: SET VOTING DATE & TIME
    # ---------------------------------------------------------------
    @app.route("/admin/schedule", methods=["GET", "POST"])
    @admin_login_required
    def admin_schedule():
        cfg = ElectionConfig.get_or_create()

        if request.method == "POST":
            start_raw = request.form.get("start_datetime")
            end_raw = request.form.get("end_datetime")
            try:
                start_dt = datetime.strptime(start_raw, "%Y-%m-%dT%H:%M")
                end_dt = datetime.strptime(end_raw, "%Y-%m-%dT%H:%M")
            except (TypeError, ValueError):
                flash("Please provide a valid start and end date/time.", "error")
                return render_template("admin_schedule.html", cfg=cfg)

            if end_dt <= start_dt:
                flash("End time must be after start time.", "error")
                return render_template("admin_schedule.html", cfg=cfg)

            cfg.start_datetime = start_dt
            cfg.end_datetime = end_dt
            db.session.commit()

            # Notify every approved voter of the day/time to cast their vote.
            schedule_msg = (
                f"Voting is scheduled from {start_dt.strftime('%B %d, %Y at %I:%M %p')} "
                f"to {end_dt.strftime('%B %d, %Y at %I:%M %p')}. Be sure to cast your vote in this window!"
            )
            approved_voters = User.query.filter_by(status="approved").all()
            for voter in approved_voters:
                db.session.add(Notification(user_id=voter.id, message=schedule_msg, kind="info"))
            db.session.commit()

            flash("Voting schedule saved and approved voters notified.", "success")
            return redirect(url_for("admin_schedule"))

        return render_template("admin_schedule.html", cfg=cfg)

    @app.route("/admin/logout")
    def admin_logout():
        session.clear()
        return redirect(url_for("home"))


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
