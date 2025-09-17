from app import create_app, db

# Create the Flask application
app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

if __name__ == '__main__':
    import os
    host = os.getenv("HOST", "0.0.0.0")  # Changed from "127.0.0.1" to "0.0.0.0"
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
