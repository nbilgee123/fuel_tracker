from app import create_app, db
from app.models import User

def create_admin_user():
    """Admin хэрэглэгч үүсгэх"""
    app = create_app()
    
    with app.app_context():
        try:
            # Admin хэрэглэгч байгаа эсэхийг шалгах
            existing_admin = User.query.filter_by(license_number='0000АДМ').first()
            
            if existing_admin:
                print("⚠️ Admin хэрэглэгч аль хэдийн байна!")
                print(f"   Улсын дугаар: {existing_admin.license_number}")
                print(f"   Админ эрх: {'Тийм' if existing_admin.is_admin else 'Үгүй'}")
                return
            
            # Шинэ admin хэрэглэгч үүсгэх
            admin = User(license_number='0000АДМ')
            admin.set_password('admin123')
            admin.is_admin = True
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin хэрэглэгч амжилттай үүсгэгдлээ!")
            print(f"   Улсын дугаар: 0000АДМ")
            print(f"   Нууц үг: admin123")
            print(f"   Админ эрх: Тийм")
            print("\n🌐 Одоо https://fuel-tracker-spt6.onrender.com/login руу орж нэвтэрч болно!")
            
        except Exception as e:
            print(f"❌ Алдаа гарлаа: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_admin_user()
