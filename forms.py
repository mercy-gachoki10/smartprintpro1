from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from wtforms.validators import ValidationError
from wtforms.widgets import CheckboxInput, ListWidget

from models import USER_MODELS, find_user_by_email


# Custom widget for checkbox list
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class RegistrationForm(FlaskForm):
    full_name = StringField(
        "Full name",
        validators=[Optional(), Length(min=3, max=120)],
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
        validators=[Optional(), Length(max=120)],
    )
    
    # Vendor-specific fields
    business_name = StringField(
        "Business name",
        validators=[Optional(), Length(max=200)],
    )
    business_address = StringField(
        "Business address",
        validators=[Optional(), Length(max=300)],
    )
    business_type = SelectField(
        "Business type",
        choices=[
            ("", "Select type (optional)"),
            ("print_shop", "Print Shop"),
            ("copy_center", "Copy Center"),
            ("design_studio", "Design & Print Studio"),
            ("signage", "Signage & Banners"),
            ("merchandise", "Merchandise & Branding"),
            ("other", "Other")
        ],
        validators=[Optional()],
    )
    services_offered = MultiCheckboxField(
        "Services offered",
        choices=[
            ("document_printing", "Document Printing"),
            ("photo_printing", "Photo Printing"),
            ("large_format", "Large Format Printing"),
            ("banners_signage", "Banners & Signage"),
            ("business_cards", "Business Cards"),
            ("flyers_brochures", "Flyers & Brochures"),
            ("booklets", "Booklets & Binding"),
            ("custom_merchandise", "Custom Merchandise"),
            ("tshirts_uniforms", "T-Shirts & Uniforms"),
            ("mugs_gifts", "Mugs & Gifts"),
            ("stickers_labels", "Stickers & Labels"),
            ("canvas_framing", "Canvas & Framing"),
            ("design_services", "Design Services"),
            ("lamination", "Lamination"),
            ("scanning", "Scanning & Digitization"),
        ],
        validators=[Optional()],
    )
    tax_id = StringField(
        "Business registration/Tax ID",
        validators=[Optional(), Length(max=50)],
    )
    
    user_type = SelectField(
        "Account type",
        choices=[("customer", "Customer"), ("vendor", "Vendor")],
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
    
    def validate_full_name(self, field):
        # Full name is required for customers only
        if self.user_type.data == "customer" and not field.data:
            raise ValidationError("Full name is required for customer accounts.")
    
    def validate_business_name(self, field):
        # Business name is required for vendors only
        if self.user_type.data == "vendor" and not field.data:
            raise ValidationError("Business name is required for vendor accounts.")

    def to_model(self):
        model = USER_MODELS[self.user_type.data]
        
        # For vendors, use business_name as full_name
        if self.user_type.data == "vendor":
            business_name = (self.business_name.data or "").strip()
            
            # Convert services list to comma-separated string
            services_list = self.services_offered.data if self.services_offered.data else []
            services_str = ",".join(services_list) if services_list else None
            
            user = model(
                full_name=business_name,  # Use business name as full name
                email=self.email.data.lower(),
                phone=self.phone.data.strip(),
                organization=None,  # Vendors don't use organization field
                business_name=business_name,
                business_address=(self.business_address.data or "").strip() or None,
                business_type=(self.business_type.data or "").strip() or None,
                services_offered=services_str,
                tax_id=(self.tax_id.data or "").strip() or None,
            )
        else:
            # For customers, use traditional fields
            user = model(
                full_name=self.full_name.data.strip(),
                email=self.email.data.lower(),
                phone=self.phone.data.strip(),
                organization=(self.organization.data or "").strip() or None,
            )
        
        return user


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
        if not user or user.user_type not in {"customer", "vendor"}:
            raise ValidationError("Only registered vendors and customers can request a reset.")
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
