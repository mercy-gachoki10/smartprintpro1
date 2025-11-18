from datetime import datetime

from flask_login import UserMixin

from extension import db


class AbstractUser(UserMixin, db.Model):
    """Base fields shared by all user tables."""

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    organization = db.Column(db.String(120))
    password_hash = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_type: str | None = None

    @property
    def is_active(self) -> bool:  # used by Flask-Login
        return bool(self.active)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.email}>"

    def get_id(self) -> str:
        """Combine user type with primary key to keep identifiers unique."""

        return f"{self.user_type}:{self.id}"


class Customer(AbstractUser):
    __tablename__ = "customers"
    user_type = "customer"


class StaffMember(AbstractUser):
    __tablename__ = "staff_members"
    user_type = "staff"


class Admin(AbstractUser):
    __tablename__ = "admins"
    user_type = "admin"


class PasswordResetRequest(db.Model):
    __tablename__ = "password_reset_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)
    admin_note = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey("admins.id"))

    resolver = db.relationship("Admin", foreign_keys=[resolved_by])

    def mark_completed(self, admin: Admin | None = None):
        self.status = "completed"
        self.resolved_at = datetime.utcnow()
        self.resolver = admin


USER_MODELS = {
    "customer": Customer,
    "staff": StaffMember,
    "admin": Admin,
}


def get_user_model(user_type: str):
    return USER_MODELS.get(user_type)


def find_user_by_email(email: str):
    """Search every user table for the provided email."""

    for model in USER_MODELS.values():
        user = model.query.filter_by(email=email).first()
        if user:
            return user
    return None


def load_user_from_identity(identity: str | None):
    if not identity or ":" not in identity:
        return None

    user_type, raw_id = identity.split(":", 1)
    model = get_user_model(user_type)
    if not model:
        return None

    return db.session.get(model, int(raw_id))
