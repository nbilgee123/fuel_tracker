from app import create_app, db
from app.models import User, FillUp, Vehicle, TriPoint
import os

def migrate_to_postgresql():
    """SQLite-аас PostgreSQL руу migrate хийх"""
    app = create_app()
    
    with app.app_context():
        try:
            # Database tables үүсгэх
            db.create_all()
            print("✅ PostgreSQL database tables үүсгэгдлээ!")
            
            # Admin хэрэглэгч үүсгэх
            admin = User.query.filter_by(license_number='0000АДМ').first()
            if not admin:
                admin = User(license_number='0000АДМ')
                admin.set_password('admin123')
                admin.is_admin = True
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin хэрэглэгч үүсгэгдлээ!")
            else:
                print("ℹ️ Admin хэрэглэгч аль хэдийн байна.")
            
            print("✅ PostgreSQL migration амжилттай!")
            
        except Exception as e:
            print(f"❌ Migration алдаа: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_to_postgresql()
