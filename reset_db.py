from app import create_app, db
from app.models import FillUp

def reset_database():
    """Reset the database - useful for testing"""
    app = create_app()
    
    with app.app_context():
        # Show current data
        fillups = FillUp.query.all()
        print(f"Current fill-ups in database: {len(fillups)}")
        
        for fillup in fillups:
            print(f"  - {fillup.date.strftime('%Y-%m-%d')}: {fillup.odometer_km}km, {fillup.fuel_liters}L")
        
        # Ask for confirmation
        choice = input("\nDo you want to delete all fill-ups? (y/N): ").lower()
        
        if choice == 'y':
            # Delete all fill-ups
            FillUp.query.delete()
            db.session.commit()
            print("✅ All fill-ups deleted!")
            print("You can now start fresh with any odometer reading.")
        else:
            print("Database left unchanged.")

if __name__ == '__main__':
    reset_database()