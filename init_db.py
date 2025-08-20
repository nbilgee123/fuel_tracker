from app import create_app, db
from app.models import FillUp

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

if __name__ == '__main__':
    init_database()