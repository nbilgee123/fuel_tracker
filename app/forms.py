from flask_wtf import FlaskForm
from wtforms import FloatField, DateField, TextAreaField, SubmitField, StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Optional, Length, Regexp, EqualTo, ValidationError
from flask_babel import gettext as _
from datetime import date

class FillUpForm(FlaskForm):
    """Form for adding a new fuel fill-up"""
    
    # Date of fill-up (defaults to today)
    date = DateField(_('Fill-up Date'), 
                    validators=[DataRequired()], 
                    default=date.today)
    
    # Odometer reading in kilometers
    odometer_km = FloatField(_('Odometer Reading (km)'), 
                            validators=[DataRequired(), 
                                      NumberRange(min=0, message=_("Odometer reading must be positive"))])
    
    # Fuel amount in liters
    fuel_liters = FloatField(_('Fuel Amount (liters)'), 
                           validators=[DataRequired(), 
                                     NumberRange(min=0.1, max=200, message=_("Fuel amount must be between 0.1 and 200 liters"))])
    
    # Estimated fuel in tank BEFORE this fill (optional)
    fuel_before_fillup = FloatField(_('Fuel Before Fill-up (liters)'), 
                                   validators=[Optional(), NumberRange(min=0.0, message=_('Value must be positive'))],
                                   render_kw={"placeholder": _("e.g., 12.5")})
    
    # Whether this fill resulted in a full tank
    is_full_tank = BooleanField(_('Filled to Full Tank?'))
    
    # Price per liter
    price_per_liter = FloatField(_('Price per Liter (₮)'), 
                               validators=[DataRequired(), 
                                         NumberRange(min=100.0, max=200000.0, message=_("Price must be between ₮100 and ₮20000"))])
    
    # Optional notes
    notes = TextAreaField(_('Notes (optional)'), 
                         validators=[Optional()],
                         render_kw={"placeholder": _("Gas station, driving conditions, etc.")})
    
    # Submit button
    submit = SubmitField(_('Add Fill-up'))
    
    def validate_odometer_km(self, field):
        """Custom validation to ensure odometer reading makes sense"""
        # We'll import here to avoid circular imports
        from app.models import FillUp
        
        # Check if this odometer reading already exists
        existing = FillUp.query.filter_by(odometer_km=field.data).first()
        if existing:
            raise ValidationError(_('A fill-up with this odometer reading already exists.'))
        
        # Check if this reading is less than the most recent reading
        latest = FillUp.query.order_by(FillUp.odometer_km.desc()).first()
        if latest and field.data <= latest.odometer_km:
            raise ValidationError(_('Odometer reading must be greater than your last entry (%(reading)s km). If you want to start over, please reset your data.', reading=latest.odometer_km))

class VehicleSettingsForm(FlaskForm):
    """Form for configuring vehicle settings including tank capacity"""
    
    # Vehicle name/description
    name = StringField(_('Vehicle Name'), 
                      validators=[DataRequired()],
                      render_kw={"placeholder": _("e.g., My Car, Family SUV")})
    
    # Fuel tank capacity in liters
    tank_capacity_liters = FloatField(_('Fuel Tank Capacity (liters)'), 
                                    validators=[DataRequired(), 
                                              NumberRange(min=20, max=200, message=_("Tank capacity must be between 20 and 200 liters"))],
                                    render_kw={"placeholder": _("e.g., 50.0")})
    
    # Submit button
    submit = SubmitField(_('Save Settings'))


class LoginForm(FlaskForm):
    license_number = StringField(
        _('License Number'),
        filters=[lambda x: x.strip().upper() if x else x],
        validators=[
            DataRequired(),
            Regexp(r'^\d{4}[А-ЯЁӨҮ]{3}$', message=_('Format: 4 digits followed by 3 Mongolian Cyrillic letters (e.g., 0570ОРХ)'))
        ],
    )
    password = PasswordField(_('Password'), validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField(_('Log In'))


class RegisterForm(FlaskForm):
    license_number = StringField(
        _('License Number'),
        filters=[lambda x: x.strip().upper() if x else x],
        validators=[
            DataRequired(),
            Regexp(r'^\d{4}[А-ЯЁӨҮ]{3}$', message=_('Format: 4 digits followed by 3 Mongolian Cyrillic letters (e.g., 0570ОРХ)'))
        ],
    )
    password = PasswordField(_('Password'), validators=[DataRequired(), Length(min=6, max=128)])
    password2 = PasswordField(_('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_('Register'))