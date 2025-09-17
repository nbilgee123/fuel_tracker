from app import create_app, db
from app.models import User

def create_admin_if_not_exists():
    """Admin хэрэглэгч байхгүй бол үүсгэх"""
    try:
        admin = User.query.filter_by(license_number='0000АДМ').first()
        if not admin:
            admin = User(license_number='0000АДМ')
            admin.set_password('admin123')
            admin.is_admin = True
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin хэрэглэгч үүсгэгдлээ!")
            print("   Улсын дугаар: 0000АДМ")
            print("   Нууц үг: admin123")
        else:
            print("ℹ️ Admin хэрэглэгч аль хэдийн байна.")
    except Exception as e:
        print(f"❌ Admin үүсгэхэд алдаа: {e}")

# Create the Flask application
app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
    
    # Admin хэрэглэгч үүсгэх (production дээр)
    create_admin_if_not_exists()

if __name__ == '__main__':
    import os
    host = os.getenv("HOST", "0.0.0.0")  # Changed from "127.0.0.1" to "0.0.0.0"
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
