from app import app, db

print("app object:", app)

try:
    with app.app_context():
        print("Inside app.app_context()")
        print("Database URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))
        db.create_all()
        print("✅ db.create_all() executed successfully!")
except Exception as e:
    import traceback
    print("❌ Error:")
    traceback.print_exc()
