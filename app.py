import os

from flask import (
    Flask,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from config import DevelopmentConfig
from decorators import roles_required
from extension import db, init_extensions, login_manager
from forms import (
    AccountUpdateForm,
    AdminPasswordResetForm,
    AdminUserEditForm,
    ForgotPasswordForm,
    LoginForm,
    RegistrationForm,
)
from models import (
    Admin,
    Customer,
    PasswordResetRequest,
    StaffMember,
    USER_MODELS,
    find_user_by_email,
    load_user_from_identity,
)
from sqlalchemy.exc import OperationalError


def create_app(config_class: type[DevelopmentConfig] | None = None):
    app = Flask(__name__)
    app.config.from_object(config_class or DevelopmentConfig)

    init_extensions(app)
    login_manager.login_view = "login"
    login_manager.user_loader(load_user_from_identity)

    register_routes(app)

    with app.app_context():
        db.create_all()
        seed_admin()

    return app


def register_routes(app: Flask):
    @app.context_processor
    def inject_helpers():
        dashboard_link = url_for("dashboard") if current_user.is_authenticated else None
        account_url = (
            url_for("edit_account")
            if current_user.is_authenticated and current_user.user_type in {"customer", "staff"}
            else None
        )
        return {
            "dashboard_url": dashboard_link,
            "account_settings_url": account_url,
        }

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/vendors")
    def vendors():
        return render_template("vendors.html")

    @app.route("/features")
    def features():
        return render_template("features.html")

    @app.route("/how-it-works")
    def how_it_works():
        return render_template("how_it_works.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        form = RegistrationForm()
        if not form.user_type.data:
            form.user_type.data = form.user_type.choices[0][0]
        if form.validate_on_submit():
            user = form.to_model()
            user.password_hash = generate_password_hash(form.password.data.strip())
            db.session.add(user)
            db.session.commit()

            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("signup.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        form = LoginForm()
        if form.validate_on_submit():
            user = find_user_by_email(form.email.data.lower())
            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=form.remember.data)
                flash(f"Welcome back, {user.full_name.split()[0]}!", "success")
                return redirect(url_for("dashboard"))

            flash("Invalid email or password.", "error")

        return render_template("login.html", form=form)

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            user = form.user
            pending = PasswordResetRequest.query.filter_by(user_id=user.id, status="pending").first()
            if pending:
                flash("You already have a pending reset request. Our admin team will contact you soon.", "info")
            else:
                reset_request = PasswordResetRequest(
                    user_id=user.id,
                    user_type=user.user_type,
                    email=user.email,
                )
                db.session.add(reset_request)
                db.session.commit()
                flash("Password reset request sent to the admin team. They'll update your password shortly.", "success")
                return redirect(url_for("login"))

        return render_template("forgotpassword.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        template = {
            "customer": "user/userdash.html",
            "staff": "staff/staffdash.html",
            "admin": "admin/admindash.html",
        }.get(current_user.user_type)

        if not template:
            flash("Unknown user type.", "error")
            return redirect(url_for("login"))

        extra_context = {}
        if current_user.user_type == "admin":
            extra_context["user_counts"] = {
                "customers": Customer.query.count(),
                "staff": StaffMember.query.count(),
                "admins": Admin.query.count(),
            }
            extra_context["pending_reset_count"] = PasswordResetRequest.query.filter_by(status="pending").count()

        return render_template(template, user=current_user, **extra_context)

    @app.route("/admin/overview")
    @roles_required("admin")
    def admin_overview():
        user_counts = {
            "customers": Customer.query.count(),
            "staff": StaffMember.query.count(),
            "admins": Admin.query.count(),
        }
        pending_reset_count = PasswordResetRequest.query.filter_by(status="pending").count()
        return render_template(
            "admin/admindash.html",
            user=current_user,
            user_counts=user_counts,
            pending_reset_count=pending_reset_count,
        )

    @app.route("/admin/users")
    @roles_required("admin")
    def admin_users():
        customers = Customer.query.order_by(Customer.created_at.desc()).all()
        staff_members = StaffMember.query.order_by(StaffMember.created_at.desc()).all()
        admins = Admin.query.order_by(Admin.created_at.desc()).all()

        user_counts = {
            "customers": len(customers),
            "staff": len(staff_members),
            "admins": len(admins),
        }

        return render_template(
            "admin/usermanagement.html",
            customers=customers,
            staff_members=staff_members,
            admins=admins,
            user_counts=user_counts,
        )

    @app.route("/admin/users/<string:user_type>/<int:user_id>/edit", methods=["GET", "POST"])
    @roles_required("admin")
    def admin_edit_user(user_type: str, user_id: int):
        from models import get_user_model

        model = get_user_model(user_type)
        if not model:
            flash("Unknown user type.", "error")
            return redirect(url_for("admin_users"))

        user = model.query.get_or_404(user_id)

        form = AdminUserEditForm(obj=user)
        if form.validate_on_submit():
            user.full_name = form.full_name.data.strip()
            user.phone = form.phone.data.strip()
            user.organization = (form.organization.data or "").strip() or None
            user.active = bool(form.active.data)
            db.session.commit()
            flash("User updated successfully.", "success")
            return redirect(url_for("admin_users"))

        return render_template("admin/edit_user.html", form=form, user=user, user_type=user_type)

    @app.route("/admin/password-requests")
    @roles_required("admin")
    def admin_password_requests():
        pending_requests = (
            PasswordResetRequest.query.filter_by(status="pending")
            .order_by(PasswordResetRequest.created_at.asc())
            .all()
        )
        recent_requests = (
            PasswordResetRequest.query.filter(PasswordResetRequest.status != "pending")
            .order_by(PasswordResetRequest.resolved_at.desc(), PasswordResetRequest.created_at.desc())
            .limit(10)
            .all()
        )

        return render_template(
            "admin/password_requests.html",
            pending_requests=pending_requests,
            recent_requests=recent_requests,
        )

    @app.route("/admin/password-requests/<int:request_id>", methods=["GET", "POST"])
    @roles_required("admin")
    def admin_password_request_detail(request_id: int):
        reset_request = PasswordResetRequest.query.get_or_404(request_id)
        form = AdminPasswordResetForm()

        if form.validate_on_submit():
            if reset_request.status == "completed":
                flash("This request has already been closed.", "info")
            else:
                model = USER_MODELS.get(reset_request.user_type)
                user = db.session.get(model, reset_request.user_id) if model else None
                if not user:
                    flash("Original user record could not be found.", "error")
                else:
                    user.password_hash = generate_password_hash(form.new_password.data.strip())
                    reset_request.mark_completed(current_user)
                    reset_request.admin_note = (form.admin_note.data or "").strip() or None
                    db.session.commit()
                    flash("Password updated and request closed.", "success")
                    return redirect(url_for("admin_password_requests"))

        return render_template(
            "admin/password_request_detail.html",
            form=form,
            reset_request=reset_request,
        )

    @app.route("/account/edit", methods=["GET", "POST"])
    @roles_required("customer", "staff")
    def edit_account():
        form = AccountUpdateForm(obj=current_user)

        if form.validate_on_submit():
            current_user.full_name = form.full_name.data.strip()
            current_user.phone = form.phone.data.strip()
            current_user.organization = (form.organization.data or "").strip() or None
            if form.new_password.data:
                current_user.password_hash = generate_password_hash(form.new_password.data.strip())

            db.session.commit()
            flash("Account details updated.", "success")
            return redirect(url_for("dashboard"))

        if not form.is_submitted():
            form.organization.data = current_user.organization or ""

        template_map = {
            "customer": "user/edit_account.html",
            "staff": "staff/edit_account.html",
        }
        template_name = template_map.get(current_user.user_type)
        if not template_name:
            flash("Unable to determine the correct account page.", "error")
            return redirect(url_for("dashboard"))

        return render_template(template_name, form=form, user=current_user)


def seed_admin():
    default_email = os.getenv("ADMIN_EMAIL", "admin@smartprintpro.com")
    default_password = os.getenv("ADMIN_PASSWORD", "Admin@123")

    try:
        existing = Admin.query.filter_by(email=default_email).first()
    except OperationalError as exc:
        db.session.rollback()
        current_app.logger.warning("Skipping default admin seed until migrations run: %s", exc)
        return

    if existing:
        return

    admin = Admin(
        full_name=os.getenv("ADMIN_NAME", "System Administrator"),
        email=default_email,
        phone=os.getenv("ADMIN_PHONE", "+254700000000"),
        organization="SmartPrint Pro",
    )
    admin.password_hash = generate_password_hash(default_password)
    db.session.add(admin)
    db.session.commit()


app = create_app()


if __name__ == "__main__":
    app.run()