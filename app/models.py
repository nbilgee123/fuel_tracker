from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, date

# Import db from flask_sqlalchemy to avoid circular imports
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class TriPoint(db.Model):
    """GPS цэгүүдийг хадгалах модель"""
    _tablename_ = "tri_points"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    
    # Relationship to User
    user = db.relationship('User', backref='tripoints')
    
    # Date of the tri point
    trip_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Odometer reading in kilometers
    odometer_km = db.Column(db.Float, nullable=False)
    
    # GPS accuracy in meters (optional)
    accuracy = db.Column(db.Float)
    
    def __repr__(self):
        return f'<TriPoint {self.lat:.6f}, {self.lon:.6f} at {self.trip_date}>'
    

class Vehicle(db.Model):
    """Машины тохиргоо, шатахууны савны хүчин чадал зэргийг хадгалах модель"""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Vehicle name/description
    name = db.Column(db.String(100), nullable=False, default="My Vehicle")
    
    # Fuel tank capacity in liters
    tank_capacity_liters = db.Column(db.Float, nullable=False, default=50.0)
    
    # Fuel type (Petrol, Diesel, LPG, CNG, Electric, Hybrid)
    fuel_type = db.Column(db.String(50), nullable=False, default="Petrol")
    
    # Date when settings were last updated
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to User
    user = db.relationship('User', backref='vehicles')
    
    def __repr__(self):
        return f'<Vehicle {self.name}: {self.tank_capacity_liters}L tank>'
    
    @staticmethod
    def get_current_vehicle(user_id):
        """Get the current vehicle settings, create default if none exists"""
        vehicle = Vehicle.query.filter_by(user_id=user_id).first()
        if not vehicle:
            vehicle = Vehicle(user_id=user_id)
            db.session.add(vehicle)
            db.session.commit()
        return vehicle


class User(UserMixin, db.Model):
    """Улсын дугаарыг хэрэглэгчийн нэр болгон ашигладаг нэвтрэх хэрэглэгч"""

    id = db.Column(db.Integer, primary_key=True)
    # License number used as username (unique)
    license_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    # Password hash
    password_hash = db.Column(db.String(256), nullable=False)
    # Admin role
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    # Optional created_at
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class FillUp(db.Model):
    """Шатахуун цэнэглэлтийн бүртгэл хадгалах модель"""
    
    # Primary key - unique ID for each fill-up
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship to User
    user = db.relationship('User', backref='fillups')
    
    # Date of the fill-up
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Odometer reading in kilometers
    odometer_km = db.Column(db.Float, nullable=False)
    
    # Fuel amount added at this fill-up (liters)
    fuel_liters = db.Column(db.Float, nullable=False)

    # Whether this fill-up brought the tank to full
    is_full_tank = db.Column(db.Boolean, nullable=False, default=False)

    # Estimated fuel in tank immediately BEFORE this fill-up (liters)
    fuel_before_fillup = db.Column(db.Float)
    
    # Cost per liter
    price_per_liter = db.Column(db.Float, nullable=False)
    
    # Total cost (calculated automatically)
    total_cost = db.Column(db.Float, nullable=False)
    
    # Optional notes
    notes = db.Column(db.Text)
    
    def __repr__(self):
        """How this object appears when printed (helpful for debugging)"""
        return f'<FillUp {self.date.strftime("%Y-%m-%d")}: {self.fuel_liters}L>'
    
    def calculate_efficiency(self):
        """Calculate fuel efficiency (L/100km) since previous fill-up.

        Uses a more robust method that considers tank levels:
        - If previous fill was full, assume tank_after_prev = tank capacity.
        - Else if we know previous fuel_before_fillup, use (prev_before + prev_added) capped by capacity.
        - For current-before level, use self.fuel_before_fillup when provided,
          otherwise if current fill is full, infer it as (capacity - fuel_added).
        Fallback to classic method (fuel_added at current fill) when both previous and current were full.
        """
        # Find the previous fill-up (by odometer reading)
        previous_fillup = FillUp.query.filter(
            FillUp.odometer_km < self.odometer_km
        ).filter_by(user_id=self.user_id).order_by(FillUp.odometer_km.desc()).first()

        if not previous_fillup:
            return None

        distance = self.odometer_km - previous_fillup.odometer_km
        if distance <= 0:
            return None

        vehicle = Vehicle.get_current_vehicle(self.user_id)
        tank_capacity = vehicle.tank_capacity_liters

        # Determine tank level right after previous fill
        tank_after_prev = None
        if getattr(previous_fillup, 'is_full_tank', False):
            tank_after_prev = tank_capacity
        elif getattr(previous_fillup, 'fuel_before_fillup', None) is not None:
            tank_after_prev = min(
                max(previous_fillup.fuel_before_fillup, 0.0) + max(previous_fillup.fuel_liters, 0.0),
                tank_capacity
            )

        # Determine tank level right before current fill
        if getattr(self, 'fuel_before_fillup', None) is not None:
            fuel_before_current = max(self.fuel_before_fillup, 0.0)
        else:
            fuel_before_current = None

        consumed_liters = None
        if tank_after_prev is not None and fuel_before_current is not None and tank_after_prev >= fuel_before_current:
            consumed_liters = tank_after_prev - fuel_before_current
        elif getattr(self, 'is_full_tank', False) and getattr(previous_fillup, 'is_full_tank', False):
            # Classic method when both fills are full: fuel added now ~= fuel consumed since last
            consumed_liters = max(self.fuel_liters, 0.0)

        if consumed_liters and consumed_liters > 0:
            return (consumed_liters / distance) * 100.0
        return None
    
    def get_remaining_fuel(self):
        """Calculate remaining fuel for this specific fill-up.
        
        For historical fill-ups: returns the fuel level right after this fill-up
        For the latest fill-up: returns the fuel level right after this fill-up (current status calculated separately)
        """
        vehicle = Vehicle.get_current_vehicle(self.user_id)
        tank_capacity = vehicle.tank_capacity_liters
        
        # Calculate what the fuel level was right after this fill-up
        if getattr(self, 'is_full_tank', False):
            return tank_capacity
        else:
            fuel_before = getattr(self, 'fuel_before_fillup', 0.0) or 0.0
            return min(fuel_before + self.fuel_liters, tank_capacity)
    
    def get_fuel_after_fillup(self):
        """Get the fuel level immediately after this fill-up"""
        vehicle = Vehicle.get_current_vehicle(self.user_id)
        tank_capacity = vehicle.tank_capacity_liters
        
        if getattr(self, 'is_full_tank', False):
            return tank_capacity
        else:
            fuel_before = getattr(self, 'fuel_before_fillup', 0.0) or 0.0
            return min(fuel_before + self.fuel_liters, tank_capacity)
    
    def predict_range(self):
        """Predict driving range based on current fuel and efficiency"""
        efficiency = self.calculate_efficiency()
        if not efficiency:
            return None
        
        # Get remaining fuel
        remaining_fuel = self.get_remaining_fuel()
        if remaining_fuel <= 0:
            return 0
        
        # Calculate range: (remaining fuel ÷ efficiency) × 100
        return (remaining_fuel / efficiency) * 100
    
    @staticmethod
    def get_total_spent(user_id):
        """Calculate total amount spent on fuel"""
        result = db.session.query(db.func.sum(FillUp.total_cost)).filter(FillUp.user_id == user_id).scalar()
        return result or 0.0
    
    @staticmethod
    def get_average_efficiency(user_id):
        """Calculate average fuel efficiency across all fill-ups"""
        fillups = FillUp.query.filter_by(user_id=user_id).order_by(FillUp.odometer_km).all()
        
        if len(fillups) < 2:
            return None
            
        total_distance = 0
        total_fuel = 0
        
        for i in range(1, len(fillups)):
            distance = fillups[i].odometer_km - fillups[i-1].odometer_km
            fuel = fillups[i].fuel_liters
            
            if distance > 0:  # Valid distance
                total_distance += distance
                total_fuel += fuel
        
        if total_distance > 0:
            return (total_fuel / total_distance) * 100  # L/100km
        return None
    
    @staticmethod
    def get_current_fuel_status(user_id):
        """Get current fuel status and predictions"""
        # Get all fill-ups ordered by odometer (oldest first)
        fillups = FillUp.query.filter_by(user_id=user_id).order_by(FillUp.odometer_km.asc()).all()
        
        if not fillups:
            return None
        
        vehicle = Vehicle.get_current_vehicle(user_id)
        efficiency = FillUp.get_average_efficiency(user_id)
        
        if not efficiency:
            return None
        
        # Get the latest fill-up
        latest_fillup = fillups[-1]
        
        # Calculate the TOTAL fuel in the tank right now
        # Start with the fuel level after the latest fill-up
        if getattr(latest_fillup, 'is_full_tank', False):
            current_fuel = vehicle.tank_capacity_liters
        else:
            fuel_before = getattr(latest_fillup, 'fuel_before_fillup', 0.0) or 0.0
            current_fuel = min(fuel_before + latest_fillup.fuel_liters, vehicle.tank_capacity_liters)
        
        # Now we need to subtract ALL fuel consumed since the latest fill-up
        # Get current odometer reading (either from GPS or use the latest fill-up as reference)
        current_odometer = FillUp.get_current_odometer_from_gps(user_id)
        
        if current_odometer and current_odometer > latest_fillup.odometer_km:
            # We have real distance data - calculate actual consumption since last fill-up
            distance_driven = current_odometer - latest_fillup.odometer_km
            fuel_consumed = (efficiency / 100.0) * distance_driven
            
            # Calculate remaining fuel: fuel after fill-up MINUS fuel consumed since then
            remaining_fuel = max(0.0, current_fuel - fuel_consumed)
            
            # Store the calculation details
            distance_driven_actual = distance_driven
            fuel_consumed_actual = fuel_consumed
            days_since_fillup = (date.today() - latest_fillup.date.date()).days
            estimated_daily_consumption = None
            
        else:
            # No GPS data - estimate based on time since last fill-up
            days_since_fillup = (date.today() - latest_fillup.date.date()).days
            
            if days_since_fillup > 0:
                # Estimate daily fuel consumption based on average efficiency
                # Assume average daily driving of 30km (adjust as needed)
                estimated_daily_distance = 30  # km per day
                estimated_daily_consumption = (efficiency / 100.0) * estimated_daily_distance
                estimated_total_consumption = estimated_daily_consumption * days_since_fillup
                
                # Calculate remaining fuel: fuel after fill-up MINUS estimated consumption
                remaining_fuel = max(0.0, current_fuel - estimated_total_consumption)
                
                # Store the calculation details
                distance_driven_actual = None
                fuel_consumed_actual = estimated_total_consumption
                
            else:
                # Fill-up was today, so use the fuel level after fill-up
                remaining_fuel = current_fuel
                distance_driven_actual = None
                fuel_consumed_actual = 0.0
                estimated_daily_consumption = 0.0
        
        fuel_percentage = (remaining_fuel / vehicle.tank_capacity_liters) * 100
        
        # Calculate predicted range
        predicted_range = (remaining_fuel / efficiency) * 100
        
        return {
            'remaining_fuel': remaining_fuel,
            'fuel_percentage': fuel_percentage,
            'tank_capacity': vehicle.tank_capacity_liters,
            'predicted_range': predicted_range,
            'efficiency': efficiency,
            'last_fillup_date': latest_fillup.date,
            'last_odometer': latest_fillup.odometer_km,
            'current_odometer': current_odometer,
            'distance_driven': distance_driven_actual,
            'fuel_consumed_since_last_fillup': fuel_consumed_actual,
            'fuel_after_last_fillup': current_fuel,
            'days_since_fillup': days_since_fillup,
            'estimated_daily_consumption': estimated_daily_consumption
        }
    
    @staticmethod
    def get_current_odometer_from_gps(user_id):
        """Get current odometer reading from GPS tracking data"""
        from app.models import TriPoint
        
        # Get the latest GPS point
        latest_point = TriPoint.query.filter_by(user_id=user_id).order_by(TriPoint.trip_date.desc()).first()
        
        if latest_point and hasattr(latest_point, 'odometer_km') and latest_point.odometer_km:
            return latest_point.odometer_km
        
        # If no GPS odometer data, return None
        return None
    
    @staticmethod
    def get_current_fuel_level(user_id):
        """Get the current fuel level in the tank based on the latest fill-up and estimated consumption"""
        fuel_status = FillUp.get_current_fuel_status(user_id)
        if fuel_status:
            return fuel_status['remaining_fuel']
        return 0.0