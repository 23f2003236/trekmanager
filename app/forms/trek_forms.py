"""Trek and booking related WTForms."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    IntegerField,
    FloatField,
    DateField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)

from app.models import DifficultyEnum, TrekStatus


class TrekForm(FlaskForm):
    """Create / edit trek form used by the admin."""

    name = StringField("Trek Name", validators=[DataRequired(), Length(max=150)])
    location = StringField("Location", validators=[DataRequired(), Length(max=150)])
    difficulty = SelectField(
        "Difficulty",
        choices=[(d, d) for d in DifficultyEnum.ALL],
        validators=[DataRequired()],
    )
    description = TextAreaField("Description", validators=[Optional(), Length(max=2000)])
    price = FloatField("Price (₹)", validators=[DataRequired(), NumberRange(min=0)])
    duration = IntegerField(
        "Duration (days)", validators=[DataRequired(), NumberRange(min=1, max=90)]
    )
    start_date = DateField("Start Date", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])
    slots = IntegerField(
        "Total Slots", validators=[DataRequired(), NumberRange(min=1, max=500)]
    )
    status = SelectField(
        "Status",
        choices=[(s, s.capitalize()) for s in TrekStatus.ALL],
        validators=[DataRequired()],
    )
    staff_id = SelectField("Assign Guide", coerce=int, validators=[Optional()])
    image = FileField(
        "Cover Image",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only.")],
    )
    submit = SubmitField("Save Trek")

    def validate_end_date(self, field):
        """Ensure the trek ends on or after it starts."""
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError("End date cannot be before the start date.")


class SlotsForm(FlaskForm):
    """Staff form to adjust total slot capacity."""

    slots = IntegerField(
        "New Capacity", validators=[DataRequired(), NumberRange(min=1, max=500)]
    )
    submit = SubmitField("Update Capacity")


class BookingForm(FlaskForm):
    """User form to confirm a booking with optional remarks."""

    remarks = TextAreaField(
        "Special requests (optional)", validators=[Optional(), Length(max=255)]
    )
    submit = SubmitField("Confirm Booking")


class SearchForm(FlaskForm):
    """Generic search / filter form used on listing pages."""

    keyword = StringField("Search", validators=[Optional()])
    location = StringField("Location", validators=[Optional()])
    difficulty = SelectField(
        "Difficulty",
        choices=[("", "All Difficulties")] + [(d, d) for d in DifficultyEnum.ALL],
        validators=[Optional()],
    )
    start_date = DateField("Start Date", validators=[Optional()])
    submit = SubmitField("Search")

    class Meta:
        csrf = False  # GET-based search form does not need CSRF.
