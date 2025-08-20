from app import create_app, db
from app.models import FillUp, Vehicle

def init_database():
    """Initialize the database with tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if we have any existing data
        fillup_count = FillUp.query.count()
        print(f"Current fill-ups in database: {fillup_count}")
        
        # Create default vehicle if none exists
        vehicle_count = Vehicle.query.count()
        if vehicle_count == 0:
            default_vehicle = Vehicle(name="My Vehicle", tank_capacity_liters=50.0)
            db.session.add(default_vehicle)
            db.session.commit()
            print("Default vehicle created with 50L tank capacity")
        else:
            print(f"Current vehicles in database: {vehicle_count}")

if __name__ == '__main__':
    init_database()