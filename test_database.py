from app import create_app, db
from app.models import User
import os

def test_database_connection():
    """Database connection шалгах"""
    app = create_app()
    
    with app.app_context():
        try:
            # Database connection шалгах
            result = db.session.execute(db.text("SELECT 1")).scalar()
            print(f"✅ Database connection амжилттай! Result: {result}")
            
            # Database type шалгах
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            if 'postgresql' in db_url:
                print("✅ PostgreSQL database ашиглаж байна")
            elif 'sqlite' in db_url:
                print("ℹ️ SQLite database ашиглаж байна")
            
            # Admin хэрэглэгч шалгах
            admin = User.query.filter_by(license_number='0000АДМ').first()
            if admin:
                print("✅ Admin хэрэглэгч байна!")
                print(f"   Улсын дугаар: {admin.license_number}")
                print(f"   Админ эрх: {'Тийм' if admin.is_admin else 'Үгүй'}")
            else:
                print("❌ Admin хэрэглэгч байхгүй!")
                
        except Exception as e:
            print(f"❌ Database connection алдаа: {e}")

if __name__ == '__main__':
    test_database_connection()
