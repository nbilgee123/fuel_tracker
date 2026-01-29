from flask_wtf import FlaskForm
from wtforms import FloatField, DateField, TextAreaField, SubmitField, StringField, BooleanField, PasswordField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional, Length, Regexp, EqualTo, ValidationError
from flask_babel import gettext as _
from datetime import date

class FillUpForm(FlaskForm):
    """Шатахуун цэнэглэлт нэмэх форм"""
    
    # Цэнэглэлтийн огноо (өнөөдөр)
    date = DateField(_('Цэнэглэлтийн огноо'), 
                    validators=[DataRequired()], 
                    default=date.today)
    
    # Одометрийн уншилт (километр)
    odometer_km = FloatField(_('Одометрийн уншилт (км)'), 
                            validators=[DataRequired(), 
                                      NumberRange(min=0, message=_("Одометрийн уншилт эерэг байх ёстой"))])
    
    # Шатахууны хэмжээ (литр)
    fuel_liters = FloatField(_('Шатахууны хэмжээ (л)'), 
                           validators=[DataRequired(), 
                                     NumberRange(min=0.1, max=200, message=_("Шатахууны хэмжээ 0.1-200 литр хооронд байх ёстой"))])
    
    # Цэнэглэхээс өмнөх шатахууны хэмжээ (сонголттой)
    fuel_before_fillup = FloatField(_('Цэнэглэхээс өмнөх шатахуун (л)'), 
                                   validators=[Optional(), NumberRange(min=0.0, message=_('Утга эерэг байх ёстой'))],
                                   render_kw={"placeholder": _("жишээ: 12.5")})
    
    # Бүрэн цэнэглэсэн эсэх
    is_full_tank = BooleanField(_('Бүрэн цэнэглэсэн үү?'))
    
    # Литр тутамд үнэ
    price_per_liter = FloatField(_('Литр тутамд үнэ (₮)'), 
                               validators=[DataRequired(), 
                                         NumberRange(min=100.0, max=200000.0, message=_("Үнэ ₮100-₮200000 хооронд байх ёстой"))])
    
    # Сонголттой тэмдэглэл
    notes = TextAreaField(_('Тэмдэглэл (сонголттой)'), 
                         validators=[Optional()],
                         render_kw={"placeholder": _("Шатахууны станц, жолооны нөхцөл гэх мэт")})
    
    # Илгээх товч
    submit = SubmitField(_('Цэнэглэлт нэмэх'))
    
    def validate_odometer_km(self, field):
        """Одометрийн уншилт зөв эсэхийг шалгах"""
        # Цикл импорт-оос зайлсхийхийн тулд энд импорт хийнэ
        from app.models import FillUp
        from flask_login import current_user
        
        # Энэ одометрийн уншилт аль хэдийн байгаа эсэхийг шалгах
        existing = FillUp.query.filter_by(user_id=getattr(current_user, 'id', None), odometer_km=field.data).first() if getattr(current_user, 'is_authenticated', False) else None
        if existing:
            raise ValidationError(_('Энэ одометрийн уншилттай цэнэглэлт аль хэдийн байна.'))
        
        # Энэ уншилт сүүлчийн уншилтаас бага эсэхийг шалгах
        latest = (
            FillUp.query.filter_by(user_id=current_user.id).order_by(FillUp.odometer_km.desc()).first()
            if getattr(current_user, 'is_authenticated', False) else None
        )
        if latest and field.data <= latest.odometer_km:
            raise ValidationError(_('Одометрийн уншилт сүүлчийн оруулснаас их байх ёстой (%(reading)s км). Дахин эхлэхийг хүсвэл өгөгдлөө шинэчлээрэй.', reading=latest.odometer_km))

class VehicleSettingsForm(FlaskForm):
    """Машины тохиргоо, шатахууны савны хүчин чадал зэргийг тохируулах форм"""
    
    # Машины нэр/тайлбар
    name = StringField(_('Машины нэр'), 
                      validators=[DataRequired()],
                      render_kw={"placeholder": _("жишээ: Миний машин, Гэр бүлийн SUV")})
    
    # Шатахууны төрөл
    fuel_type = SelectField(_('Шатахууны төрөл'), 
                           choices=[
                               ('Petrol', _('Бензин')),
                               ('Diesel', _('Дизель')),
                               ('Electric', _('Цахилгаан')),
                               ('Hybrid', _('Hybrid'))
                           ],
                           validators=[DataRequired()])
    
    # Шатахууны савны хүчин чадал (литр)
    tank_capacity_liters = FloatField(_('Шатахууны савны хүчин чадал (л)'), 
                                    validators=[DataRequired(), 
                                              NumberRange(min=20, max=200, message=_("Савны хүчин чадал 20-200 литр хооронд байх ёстой"))],
                                    render_kw={"placeholder": _("жишээ: 50.0")})
    
    # Хадгалах товч
    submit = SubmitField(_('Тохиргоо хадгалах'))


class LoginForm(FlaskForm):
    license_number = StringField(
        _('Улсын дугаар'),
        filters=[lambda x: x.strip().upper() if x else x],
        validators=[
            DataRequired(),
            Regexp(r'^\d{4}[А-ЯЁӨҮ]{3}$', message=_('Формат: 4 орон + 3 монгол үсэг (жишээ: 0570ОРХ)'))
        ],
    )
    password = PasswordField(_('Нууц үг'), validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField(_('Нэвтрэх'))


class RegisterForm(FlaskForm):
    license_number = StringField(
        _('Улсын дугаар'),
        filters=[lambda x: x.strip().upper() if x else x],
        validators=[
            DataRequired(),
            Regexp(r'^\d{4}[А-ЯЁӨҮ]{3}$', message=_('Формат: 4 орон + 3 монгол үсэг (жишээ: 0570ОРХ)'))
        ],
    )
    password = PasswordField(_('Нууц үг'), validators=[DataRequired(), Length(min=6, max=128)])
    password2 = PasswordField(_('Нууц үг давтах'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_('Бүртгүүлэх'))


class AdminPasswordResetForm(FlaskForm):
    """Админы хэрэглэгчийн нууц үг солих форм"""
    
    new_password = PasswordField(
        _('Шинэ нууц үг'), 
        validators=[DataRequired(), Length(min=6, max=128, message=_('Нууц үг 6-128 тэмдэгттэй байх ёстой'))]
    )
    confirm_password = PasswordField(
        _('Нууц үг баталгаажуулах'), 
        validators=[DataRequired(), EqualTo('new_password', message=_('Нууц үг таарахгүй байна'))]
    )
    submit = SubmitField(_('Нууц үг солих'))