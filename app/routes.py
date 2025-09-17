from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request, send_from_directory
from flask_babel import gettext as _
from app import db
from app.models import FillUp, TriPoint, Vehicle, User
from app.forms import FillUpForm, VehicleSettingsForm, LoginForm, RegisterForm, AdminPasswordResetForm
from datetime import datetime
 
import math
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps

# Create a blueprint (think of it as a mini-app)
main = Blueprint('main', __name__)

def admin_required(f):
    """Админ эрх шаардлагатай декоратор"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash(_('Админ эрх шаардлагатай.'), 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
@login_required
def index():
    """Home page route"""
    # Get some basic stats for the homepage
    total_fillups = FillUp.query.filter_by(user_id=current_user.id).count()
    total_spent = FillUp.get_total_spent(current_user.id)
    average_efficiency = FillUp.get_average_efficiency(current_user.id)
    
    # Get current fuel status and predictions
    fuel_status = FillUp.get_current_fuel_status(current_user.id)
    
    # Get vehicle settings
    vehicle = Vehicle.get_current_vehicle(current_user.id)
    
    return render_template('index.html', 
                         total_fillups=total_fillups,
                         total_spent=total_spent,
                         average_efficiency=average_efficiency,
                         fuel_status=fuel_status,
                         vehicle=vehicle)


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(license_number=form.license_number.data).first()
        if existing:
            flash(_('Энэ улсын дугаартай бүртгэл аль хэдийн байна.'), 'error')
        else:
            user = User(license_number=form.license_number.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            # Ensure a default vehicle exists for this user
            Vehicle.get_current_vehicle(user.id)
            flash(_('Бүртгэл үүсгэгдлээ. Одоо нэвтэрч болно.'), 'success')
            return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(license_number=form.license_number.data).first()
        if user and user.check_password(form.password.data):
            # Remember login across browser sessions
            login_user(user, remember=True)
            flash(_('Амжилттай нэвтэрлээ.'), 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash(_('Буруу улсын дугаар эсвэл нууц үг.'), 'error')
    return render_template('login.html', form=form)


@main.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash(_('Гарлаа.'), 'success')
    return redirect(url_for('main.index'))

# Language switching route removed; application is fixed to Mongolian locale

@main.route('/add_fillup', methods=['GET', 'POST'])
@login_required
def add_fillup():
    """Add new fill-up route"""
    form = FillUpForm()
    
    if form.validate_on_submit():
        # Calculate total cost
        total_cost = form.fuel_liters.data * form.price_per_liter.data
        
        # Get the previous fill-up to calculate fuel_before_fillup
        previous_fillup = FillUp.query.filter_by(user_id=current_user.id).order_by(FillUp.odometer_km.desc()).first()
        
        # Calculate fuel_before_fillup automatically if not provided
        fuel_before_fillup = form.fuel_before_fillup.data
        if fuel_before_fillup is None and previous_fillup:
            # Get vehicle for efficiency calculation
            vehicle = Vehicle.get_current_vehicle(current_user.id)
            efficiency = FillUp.get_average_efficiency(current_user.id)
            
            if efficiency and previous_fillup:
                # Calculate distance since last fill-up
                distance_km = form.odometer_km.data - previous_fillup.odometer_km
                
                if distance_km > 0:
                    # Calculate fuel consumed since last fill-up
                    fuel_consumed = (efficiency / 100.0) * distance_km
                    
                    # Get fuel level after the previous fill-up
                    fuel_after_prev = previous_fillup.get_fuel_after_fillup()
                    
                    # Calculate remaining fuel before this fill-up
                    calculated_fuel_before = max(0.0, fuel_after_prev - fuel_consumed)
                    fuel_before_fillup = calculated_fuel_before
        
        # Create new fill-up record
        fillup = FillUp(
            user_id=current_user.id,
            date=form.date.data,
            odometer_km=form.odometer_km.data,
            fuel_liters=form.fuel_liters.data,
            is_full_tank=bool(getattr(form, 'is_full_tank', None) and form.is_full_tank.data),
            fuel_before_fillup=fuel_before_fillup,
            price_per_liter=form.price_per_liter.data,
            total_cost=total_cost,
            notes=form.notes.data
        )
        
        try:
            # Add to database
            db.session.add(fillup)
            db.session.commit()
            
            # Calculate efficiency if possible
            efficiency = fillup.calculate_efficiency()
            if efficiency:
                flash(_('Цэнэглэлт амжилттай нэмэгдлээ! Шатахууны хэрэглээ: %(efficiency).1f л/100км', efficiency=efficiency), 'success')
            else:
                flash(_('Цэнэглэлт амжилттай нэмэгдлээ! Шатахууны хэрэглээг харахын тулд илүү оруулга нэмнэ үү.'), 'success')
            
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Цэнэглэлт нэмэхэд алдаа гарлаа: %(error)s', error=str(e)), 'error')
    
    return render_template('add_fillup.html', form=form)

@main.route('/history')
@login_required
def history():
    """View all fill-ups in a table"""
    from app.models import FillUp
    
    fillups = FillUp.query.filter_by(user_id=current_user.id).order_by(FillUp.odometer_km.asc()).all()
    
    # Get current fuel status for display
    current_fuel_level = FillUp.get_current_fuel_level(current_user.id)
    
    return render_template('history.html', 
                         fillups=fillups,
                         current_fuel_level=current_fuel_level)

@main.route('/charts')
@login_required
def charts():
    """Display charts and analytics"""
    fillups = FillUp.query.filter_by(user_id=current_user.id).order_by(FillUp.date.asc()).all()
    
    if len(fillups) < 2:
        return render_template('charts.html', 
                         fillups=fillups,
                         spending_labels=[], spending_data=[],
                         efficiency_labels=[], efficiency_data=[],
                         volume_labels=[], volume_data=[])
    
    # Process data for charts
    from datetime import datetime
    import calendar
    from collections import defaultdict
    
    # Group data by month
    monthly_spending = defaultdict(float)
    monthly_volume = defaultdict(float)
    monthly_efficiency = []
    
    for fillup in fillups:
        month_key = fillup.date.strftime('%Y-%m')
        monthly_spending[month_key] += fillup.total_cost
        monthly_volume[month_key] += fillup.fuel_liters
    
    # Calculate efficiency for each fillup
    efficiency_labels = []
    efficiency_data = []
    
    for i, fillup in enumerate(fillups):
        if i > 0: # Skip first fillup as it has no previous reference
            efficiency = fillup.calculate_efficiency()
            if efficiency:
                efficiency_labels.append(fillup.date.strftime('%Y-%m-%d'))
                efficiency_data.append(round(efficiency, 2))
    
    # Prepare spending chart data
    spending_labels = []
    spending_data = []
    
    for month_key in sorted(monthly_spending.keys()):
        year, month = month_key.split('-')
        month_name = calendar.month_abbr[int(month)] + ' ' + year
        spending_labels.append(month_name)
        spending_data.append(round(monthly_spending[month_key], 2))
    
    # Prepare volume chart data
    volume_labels = []
    volume_data = []
    
    for month_key in sorted(monthly_volume.keys()):
        year, month = month_key.split('-')
        month_name = calendar.month_abbr[int(month)] + ' ' + year
        volume_labels.append(month_name)
        volume_data.append(round(monthly_volume[month_key], 1))
    
    # Calculate statistics
    efficiencies = [e for e in efficiency_data if e]
    best_efficiency = min(efficiencies) if efficiencies else 0
    worst_efficiency = max(efficiencies) if efficiencies else 0
    avg_price = sum(f.price_per_liter for f in fillups) / len(fillups)
    total_distance = fillups[-1].odometer_km - fillups[0].odometer_km if len(fillups) > 1 else 0
    
    return render_template('charts.html',
                         fillups=fillups,
                         spending_labels=spending_labels,
                         spending_data=spending_data,
                         efficiency_labels=efficiency_labels,
                         efficiency_data=efficiency_data,
                         volume_labels=volume_labels,
                         volume_data=volume_data,
                         best_efficiency=best_efficiency,
                         worst_efficiency=worst_efficiency,
                         avg_price=avg_price,
                         total_distance=total_distance)

@main.route('/range_predictor', methods=['GET', 'POST'])
@login_required
def range_predictor():
    """Predict driving range based on current fuel and efficiency"""
    fillups = FillUp.query.filter_by(user_id=current_user.id).order_by(FillUp.date.asc()).all()
    total_fillups = len(fillups)
    
    # Calculate efficiency statistics
    average_efficiency = FillUp.get_average_efficiency(current_user.id)
    
    if not average_efficiency or total_fillups < 2:
        return render_template('range_predictor.html',
                         average_efficiency=None,
                         total_fillups=total_fillups)
    
    # Calculate efficiency stats
    efficiencies = []
    for i in range(1, len(fillups)):
        efficiency = fillups[i].calculate_efficiency()
        if efficiency:
            efficiencies.append(efficiency)
    
    best_efficiency = min(efficiencies) if efficiencies else average_efficiency
    worst_efficiency = max(efficiencies) if efficiencies else average_efficiency
    
    predicted_range = None
    current_fuel = None
    
    if request.method == 'POST':
        try:
            current_fuel = float(request.form.get('current_fuel', 0))
            
            if current_fuel <= 0:
                flash(_('0-ээс их шатахууны хэмжээ оруулна уу.'), 'error')
            elif current_fuel > 200:
                flash(_('Шатахууны хэмжээ хэт өндөр байна. Оруулгаа шалгана уу.'), 'error')
            else:
                # Calculate predicted range: (fuel ÷ efficiency) × 100
                predicted_range = (current_fuel / average_efficiency) * 100
                
                flash(_('Зай амжилттай тооцооллоо! Таны дундаж хэрэглээ %(efficiency).1f л/100км-д тулгуурлан.', efficiency=average_efficiency), 'success')
                
        except (ValueError, TypeError):
            flash(_('Шатахууны хэмжээнд зөв тоо оруулна уу.'), 'error')
    
    return render_template('range_predictor.html',
                         average_efficiency=average_efficiency,
                         best_efficiency=best_efficiency,
                         worst_efficiency=worst_efficiency,
                         total_fillups=total_fillups,
                         predicted_range=predicted_range,
                         current_fuel=current_fuel)

@main.route('/delete_fillup/<int:id>', methods=['POST'])
@login_required
def delete_fillup(id):
    """Delete a specific fill-up"""
    fillup = FillUp.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(fillup)
        db.session.commit()
        flash(_('%(date)s-ны цэнэглэлт амжилттай устгагдлаа.', date=fillup.date.strftime("%Y-%m-%d")), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Цэнэглэлт устгахад алдаа гарлаа: %(error)s', error=str(e)), 'error')
    
    return redirect(url_for('main.history'))

@main.route('/vehicle_settings', methods=['GET', 'POST'])
@login_required
def vehicle_settings():
    """Configure vehicle settings including tank capacity"""
    form = VehicleSettingsForm()
    vehicle = Vehicle.get_current_vehicle(current_user.id)
    
    if form.validate_on_submit():
        try:
            # Update vehicle settings
            vehicle.name = form.name.data
            vehicle.tank_capacity_liters = form.tank_capacity_liters.data
            vehicle.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash(_('Машины тохиргоо амжилттай шинэчлэгдлээ!'), 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Машины тохиргоо шинэчлэхэд алдаа гарлаа: %(error)s', error=str(e)), 'error')
    
    elif request.method == 'GET':
        # Pre-populate form with current values
        form.name.data = vehicle.name
        form.tank_capacity_liters.data = vehicle.tank_capacity_liters
    
    return render_template('vehicle_settings.html', form=form, vehicle=vehicle)

@main.route("/api/location", methods=["POST"])
@login_required
def save_location():
    """Save location to database"""
    data = request.json
    lat = data.get("lat")
    lon = data.get("lon")
    accuracy = data.get("accuracy")
    timestamp_iso = data.get("timestamp")

    if lat is None or lon is None:
        return jsonify({"error": "Missing required fields"}), 400

    # Determine timestamp
    try:
        date_value = datetime.fromisoformat(timestamp_iso) if timestamp_iso else datetime.utcnow()
    except Exception:
        date_value = datetime.utcnow()

    # Compute odometer based on last point distance if available
    last_point = TriPoint.query.filter_by(user_id=current_user.id).order_by(TriPoint.trip_date.desc()).first()

    def haversine_km(lat1, lon1, lat2, lon2):
        """Calculate distance between two lat/lon points in kilometers"""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    if last_point:
        incremental_km = haversine_km(last_point.lat, last_point.lon, lat, lon)
        # Treat tiny GPS jitter as zero movement (increased threshold for better accuracy)
        if incremental_km < 0.005:  # 5 meters threshold
            incremental_km = 0.0
        odometer_km = (last_point.odometer_km or 0.0) + incremental_km
    else:
        odometer_km = 0.0
    
    # Create point with enhanced data
    point = TriPoint(
        user_id=current_user.id, 
        lat=lat, 
        lon=lon, 
        odometer_km=odometer_km, 
        trip_date=date_value
    )
    
    # Store accuracy if provided
    if accuracy is not None:
        point.accuracy = accuracy
    
    db.session.add(point)
    db.session.commit()
    
    return jsonify({
        "message": "Location saved successfully",
        "point_id": point.id,
        "odometer_km": odometer_km,
        "incremental_km": incremental_km if 'incremental_km' in locals() else 0.0
    }), 201

@main.route("/api/location", methods=["GET"])
@login_required
def get_location():
    """Get location from database"""
    limit = request.args.get("limit", type=int) or 500
    points = TriPoint.query.filter_by(user_id=current_user.id).order_by(TriPoint.trip_date.desc()).limit(limit).all()
    # Return in chronological order
    points = list(reversed(points))
    return jsonify([
        {
            "id": p.id,
            "lat": p.lat,
            "lon": p.lon,
            "odometer_km": p.odometer_km,
            "date": p.trip_date.isoformat(),
            "accuracy": getattr(p, 'accuracy', None)
        }
        for p in points
    ])


@main.route('/map')
@login_required
def map_view():
    """Render the tracking map view"""
    return render_template('map.html')


@main.route('/api/trips/stats', methods=['GET'])
@login_required
def trips_stats():
    """Return aggregate movement vs idle time and fuel estimates"""
    # Fetch recent points
    limit = request.args.get("limit", type=int) or 2000
    points = TriPoint.query.filter_by(user_id=current_user.id).order_by(TriPoint.trip_date.desc()).limit(limit).all()
    points = list(reversed(points))

    if len(points) < 2:
        return jsonify({
            "total_distance_km": 0.0,
            "moving_time_minutes": 0.0,
            "idle_time_minutes": 0.0,
            "idle_fuel_liters": 0.0,
            "moving_fuel_liters": 0.0,
            "total_fuel_liters": 0.0,
            "total_points": 0,
            "last_update": None
        })

    def haversine_km(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    total_distance_km = 0.0
    moving_time_seconds = 0.0
    idle_time_seconds = 0.0
    max_speed_kmh = 0.0
    avg_speed_kmh = 0.0
    speed_samples = 0

    # Thresholds
    speed_threshold_kmh = 2.0  # below this is considered idle
    jitter_distance_km = 0.005  # ignore GPS noise (5 meters)

    for i in range(1, len(points)):
        p1 = points[i - 1]
        p2 = points[i]
        dt = (p2.trip_date - p1.trip_date).total_seconds()
        if dt <= 0:
            continue
        d_km = haversine_km(p1.lat, p1.lon, p2.lat, p2.lon)
        if d_km < jitter_distance_km:
            d_km = 0.0
        total_distance_km += d_km
        
        if d_km > 0 and dt > 0:
            speed_kmh = (d_km / dt) * 3600.0
            if speed_kmh >= speed_threshold_kmh:
                moving_time_seconds += dt
                max_speed_kmh = max(max_speed_kmh, speed_kmh)
                avg_speed_kmh += speed_kmh
                speed_samples += 1
            else:
                idle_time_seconds += dt

    # Calculate average speed
    if speed_samples > 0:
        avg_speed_kmh = avg_speed_kmh / speed_samples

    # Fuel estimates using user's actual efficiency
    avg_eff_l_per_100km = FillUp.get_average_efficiency(current_user.id) or 10.0  # default
    moving_fuel_liters = (avg_eff_l_per_100km / 100.0) * total_distance_km

    # Idle fuel consumption (can be customized per user)
    idle_fuel_lph = 0.8  # default idle fuel consumption liters/hour
    idle_fuel_liters = idle_fuel_lph * (idle_time_seconds / 3600.0)

    return jsonify({
        "total_distance_km": round(total_distance_km, 3),
        "moving_time_minutes": round(moving_time_seconds / 60.0, 1),
        "idle_time_minutes": round(idle_time_seconds / 60.0, 1),
        "idle_fuel_liters": round(idle_fuel_liters, 2),
        "moving_fuel_liters": round(moving_fuel_liters, 2),
        "total_fuel_liters": round(idle_fuel_liters + moving_fuel_liters, 2),
        "max_speed_kmh": round(max_speed_kmh, 1),
        "avg_speed_kmh": round(avg_speed_kmh, 1),
        "total_points": len(points),
        "last_update": points[-1].trip_date.isoformat() if points else None,
        "efficiency_l_per_100km": round(avg_eff_l_per_100km, 1)
    })


@main.route('/api/trips', methods=['POST'])
@login_required
def save_trip():
    """Save completed trip data"""
    data = request.json
    
    if not data or 'distance_km' not in data or 'duration_seconds' not in data:
        return jsonify({"error": "Missing required trip data"}), 400
    
    # Here you could save trip data to a separate table
    # For now, we'll just return success
    trip_data = {
        "user_id": current_user.id,
        "start_time": data.get('start_time'),
        "end_time": data.get('end_time'),
        "distance_km": data.get('distance_km'),
        "duration_seconds": data.get('duration_seconds'),
        "fuel_consumed_liters": data.get('fuel_consumed_liters'),
        "start_location": data.get('start_location'),
        "end_location": data.get('end_location'),
        "max_speed_kmh": data.get('max_speed_kmh'),
        "avg_speed_kmh": data.get('avg_speed_kmh')
    }
    
    # Log trip data (you could save this to database)
    print(f"Trip completed: {trip_data}")
    
    return jsonify({
        "message": "Trip saved successfully",
        "trip_id": f"trip_{datetime.utcnow().timestamp()}",
        "data": trip_data
    }), 201


@main.route('/api/motor_hour', methods=['GET'])
@login_required
def motor_hour_norm():
    """Estimate engine idle consumption rate (liters/hour) between last two fill-ups.

    Approach:
    - Use last two fill-ups to define interval [prev, curr].
    - Compute distance and idle time from TriPoint samples within interval.
    - Estimate total fuel consumed from curr.calculate_efficiency() and distance.
    - Estimate moving baseline fuel using best historical efficiency.
    - idle_lph = max(total - moving_baseline, 0) / idle_hours.
    """
    fillups = FillUp.query.filter_by(user_id=current_user.id).order_by(FillUp.date.asc()).all()
    if len(fillups) < 2:
        return jsonify({"error": "Not enough fill-ups"}), 400

    prev = fillups[-2]
    curr = fillups[-1]

    # Points in window
    points = TriPoint.query.filter(TriPoint.trip_date >= prev.date, TriPoint.trip_date <= curr.date, TriPoint.user_id == current_user.id).order_by(TriPoint.trip_date.asc()).all()
    if len(points) < 2:
        return jsonify({"error": "Not enough GPS points in interval"}), 400

    def haversine_km(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    distance_km = 0.0
    idle_seconds = 0.0
    speed_threshold_kmh = 2.0
    jitter_km = 0.01

    for i in range(1, len(points)):
        p1, p2 = points[i - 1], points[i]
        dt = (p2.trip_date - p1.trip_date).total_seconds()
        if dt <= 0:
            continue
        d_km = haversine_km(p1.lat, p1.lon, p2.lat, p2.lon)
        if d_km < jitter_km:
            d_km = 0.0
        distance_km += d_km
        speed_kmh = (d_km / dt) * 3600.0
        if speed_kmh < speed_threshold_kmh:
            idle_seconds += dt

    # Total consumed in interval using current fill efficiency
    interval_eff = curr.calculate_efficiency()
    if not interval_eff:
        return jsonify({"error": "Cannot compute efficiency for interval"}), 400
    total_consumed_l = (interval_eff / 100.0) * max(distance_km, 0.0)

    # Baseline moving efficiency: best historical efficiency (lower is better)
    all_fillups = FillUp.query.filter_by(user_id=current_user.id).order_by(FillUp.date.asc()).all()
    efficiencies = []
    for i in range(1, len(all_fillups)):
        e = all_fillups[i].calculate_efficiency()
        if e:
            efficiencies.append(e)
    if not efficiencies:
        return jsonify({"error": "No efficiency data available"}), 400
    best_eff = min(efficiencies)
    moving_baseline_l = (best_eff / 100.0) * max(distance_km, 0.0)

    idle_liters = max(total_consumed_l - moving_baseline_l, 0.0)
    idle_hours = idle_seconds / 3600.0
    idle_lph = (idle_liters / idle_hours) if idle_hours > 0 else None

    return jsonify({
        "interval_start": prev.date.isoformat(),
        "interval_end": curr.date.isoformat(),
        "distance_km": round(distance_km, 3),
        "idle_hours": round(idle_hours, 2),
        "total_consumed_liters": round(total_consumed_l, 2),
        "moving_baseline_liters": round(moving_baseline_l, 2),
        "idle_liters": round(idle_liters, 2),
        "idle_liters_per_hour": round(idle_lph, 2) if idle_lph is not None else None
    })

@main.route('/api/last_fillup')
@login_required
def api_last_fillup():
    """API endpoint to get last fillup data for fuel calculation"""
    try:
        # Get the most recent fillup
        latest_fillup = FillUp.query.filter_by(user_id=current_user.id).order_by(FillUp.odometer_km.desc()).first()
        
        if not latest_fillup:
            return jsonify({
                'success': False,
                'message': 'No fillups found'
            })
        
        # Get average efficiency
        average_efficiency = FillUp.get_average_efficiency(current_user.id)
        
        # Get fuel after the last fillup using the model method
        fuel_after_fillup = latest_fillup.get_fuel_after_fillup()
        
        return jsonify({
            'success': True,
            'last_fillup': {
                'odometer_km': latest_fillup.odometer_km,
                'fuel_after_fillup': fuel_after_fillup,
                'date': latest_fillup.date.isoformat()
            },
            'average_efficiency': average_efficiency
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@main.route('/test_fuel_calculation')
@login_required
def test_fuel_calculation():
    """Test route to demonstrate fuel calculation logic"""
    try:
        # Get current fuel status
        fuel_status = FillUp.get_current_fuel_status(current_user.id)
        
        if not fuel_status:
            return jsonify({
                'success': False,
                'message': 'No fuel status available'
            })
        
        # Get the latest fillup for comparison
        latest_fillup = FillUp.query.filter_by(user_id=current_user.id).order_by(FillUp.odometer_km.desc()).first()
        
        return jsonify({
            'success': True,
            'fuel_status': fuel_status,
            'latest_fillup': {
                'odometer_km': latest_fillup.odometer_km,
                'fuel_liters': latest_fillup.fuel_liters,
                'fuel_before_fillup': getattr(latest_fillup, 'fuel_before_fillup', None),
                'is_full_tank': getattr(latest_fillup, 'is_full_tank', False),
                'date': latest_fillup.date.isoformat()
            },
            'calculation_explanation': {
                'step1': f"Fuel after last fillup: {fuel_status['fuel_after_last_fillup']:.1f}L",
                'step2': f"Fuel consumed since then: {fuel_status['fuel_consumed_since_last_fillup']:.1f}L",
                'step3': f"Remaining fuel: {fuel_status['fuel_after_last_fillup']:.1f}L - {fuel_status['fuel_consumed_since_last_fillup']:.1f}L = {fuel_status['remaining_fuel']:.1f}L"
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# Admin routes
@main.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    # Get statistics
    total_users = User.query.count()
    total_fillups = FillUp.query.count()
    total_vehicles = Vehicle.query.count()
    total_tripoints = TriPoint.query.count()
    
    # Get recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Get recent fillups
    recent_fillups = FillUp.query.order_by(FillUp.date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_fillups=total_fillups,
                         total_vehicles=total_vehicles,
                         total_tripoints=total_tripoints,
                         recent_users=recent_users,
                         recent_fillups=recent_fillups)


@main.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin users management"""
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users.html', users=users)


@main.route('/admin/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash(_('Өөрийн админ эрхээ өөрчлөх боломжгүй.'), 'error')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = _('админ') if user.is_admin else _('хэрэглэгч')
        flash(_('Хэрэглэгч %(license)s одоо %(status)s боллоо', license=user.license_number, status=status), 'success')
    return redirect(url_for('main.admin_users'))


@main.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash(_('Өөрийн бүртгэлээ устгах боломжгүй.'), 'error')
    else:
        # Delete related data
        FillUp.query.filter_by(user_id=user_id).delete()
        TriPoint.query.filter_by(user_id=user_id).delete()
        Vehicle.query.filter_by(user_id=user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        flash(_('Хэрэглэгч %(license)s амжилттай устгагдлаа.', license=user.license_number), 'success')
    return redirect(url_for('main.admin_users'))


@main.route('/admin/fillups')
@login_required
@admin_required
def admin_fillups():
    """Admin fillups management"""
    page = request.args.get('page', 1, type=int)
    fillups = FillUp.query.order_by(FillUp.date.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('admin/fillups.html', fillups=fillups)


@main.route('/admin/vehicles')
@login_required
@admin_required
def admin_vehicles():
    """Admin vehicles management"""
    vehicles = Vehicle.query.all()
    return render_template('admin/vehicles.html', vehicles=vehicles)


@main.route('/admin/users/<int:user_id>/reset_password', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """Reset password for a user"""
    user = User.query.get_or_404(user_id)
    form = AdminPasswordResetForm()
    
    if form.validate_on_submit():
        try:
            user.set_password(form.new_password.data)
            db.session.commit()
            flash(_('Хэрэглэгч %(license)s-ийн нууц үг амжилттай солигдлоо.', license=user.license_number), 'success')
            return redirect(url_for('main.admin_users'))
        except Exception as e:
            db.session.rollback()
            flash(_('Нууц үг солиход алдаа гарлаа: %(error)s', error=str(e)), 'error')
    
    return render_template('admin/reset_password.html', form=form, user=user)


# PWA Routes
@main.route('/manifest.json')
def manifest():
    """PWA manifest file"""
    return send_from_directory('static', 'manifest.json', mimetype='application/json')

@main.route('/sw.js')
def service_worker():
    """Service Worker file"""
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

@main.route('/offline')
def offline():
    """Offline page"""
    return render_template('offline.html')

@main.route('/api/sync-offline-data', methods=['POST'])
@login_required
def sync_offline_data():
    """Sync offline data when connection is restored"""
    try:
        data = request.get_json()
        offline_data = data.get('offlineData', [])
        
        # Process offline data here
        # For now, just return success
        return jsonify({'status': 'success', 'message': 'Offline data synced'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500