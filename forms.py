from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from wtforms.validators import ValidationError

from models import USER_MODELS, find_user_by_email


class RegistrationForm(FlaskForm):
    full_name = StringField(
        "Full name",
        validators=[DataRequired(), Length(min=3, max=120)],
    )
    email = StringField(
        "Email address",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    phone = StringField(
        "Phone number",
        validators=[DataRequired(), Length(min=6, max=30)],
    )
    organization = StringField(
        "Organization (optional)",
        validators=[Length(max=120)],
    )
    user_type = SelectField(
        "Account type",
        choices=[("customer", "Customer"), ("staff", "Staff")],
        validators=[DataRequired()],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8)],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create Account")

    def validate_email(self, field):
        existing = find_user_by_email(field.data.lower())
        if existing:
            raise ValidationError("That email is already registered.")

    def to_model(self):
        model = USER_MODELS[self.user_type.data]
        return model(
            full_name=self.full_name.data.strip(),
            email=self.email.data.lower(),
            phone=self.phone.data.strip(),
            organization=(self.organization.data or "").strip() or None,
        )


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log In")


class AdminUserEditForm(FlaskForm):
    full_name = StringField(
        "Full name",
        validators=[DataRequired(), Length(min=3, max=120)],
    )
    phone = StringField(
        "Phone number",
        validators=[DataRequired(), Length(min=6, max=30)],
    )
    organization = StringField(
        "Organization (optional)",
        validators=[Length(max=120)],
    )
    active = BooleanField("Active")
    submit = SubmitField("Save changes")


class ForgotPasswordForm(FlaskForm):
    email = StringField(
        "Work email",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    submit = SubmitField("Send reset request")

    user = None

    def validate_email(self, field):
        user = find_user_by_email(field.data.lower())
        if not user or user.user_type not in {"customer", "staff"}:
            raise ValidationError("Only registered staff and customers can request a reset.")
        self.user = user


class AdminPasswordResetForm(FlaskForm):
    new_password = PasswordField(
        "New password",
        validators=[DataRequired(), Length(min=8)],
    )
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match.")],
    )
    admin_note = StringField(
        "Internal note (optional)",
        validators=[Optional(), Length(max=255)],
    )
    submit = SubmitField("Update password")


class AccountUpdateForm(FlaskForm):
    full_name = StringField(
        "Full name",
        validators=[DataRequired(), Length(min=3, max=120)],
    )
    phone = StringField(
        "Phone number",
        validators=[DataRequired(), Length(min=6, max=30)],
    )
    organization = StringField(
        "Organization (optional)",
        validators=[Length(max=120)],
    )
    new_password = PasswordField(
        "New password (optional)",
        validators=[Optional(), Length(min=8)],
    )
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[Optional(), EqualTo("new_password", message="Passwords must match.")],
    )
    submit = SubmitField("Save changes")
