"""Authentication related WTForms."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SelectField,
    TextAreaField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    Regexp,
    Optional,
)

from app.models import User


class LoginForm(FlaskForm):
    """Sign-in form."""

    username = StringField(
        "Username or Email", validators=[DataRequired(), Length(max=120)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Keep me signed in")
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    """Registration form for users and staff."""

    full_name = StringField(
        "Full Name", validators=[DataRequired(), Length(min=2, max=120)]
    )
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=80),
            Regexp(
                r"^[A-Za-z0-9_.]+$",
                message="Username may contain letters, numbers, dots and underscores only.",
            ),
        ],
    )
    email = StringField(
        "Email", validators=[DataRequired(), Email(), Length(max=120)]
    )
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    role = SelectField(
        "I want to join as",
        choices=[("user", "Trekker (book adventures)"), ("staff", "Trek Guide / Staff")],
        validators=[DataRequired()],
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=128)]
    )
    confirm = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create Account")

    # Field-level uniqueness validators -----------------------------------
    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValueError("That username is already taken.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValueError("An account with that email already exists.")


class ProfileForm(FlaskForm):
    """Edit-profile form for users and staff."""

    full_name = StringField(
        "Full Name", validators=[DataRequired(), Length(min=2, max=120)]
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    bio = TextAreaField("Bio", validators=[Optional(), Length(max=500)])
    password = PasswordField(
        "New Password (leave blank to keep current)",
        validators=[Optional(), Length(min=6, max=128)],
    )
    confirm = PasswordField(
        "Confirm New Password",
        validators=[Optional(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Save Changes")

    def __init__(self, original_user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_user = original_user

    def validate_email(self, field):
        if self.original_user and field.data.strip().lower() == self.original_user.email:
            return
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValueError("An account with that email already exists.")
