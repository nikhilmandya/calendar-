from app import app, db, User
from werkzeug.security import generate_password_hash

# Set up the application context
with app.app_context():
    # Generate a hashed password
    hashed_password = generate_password_hash('admin123')

    # Create a new admin user
    admin_user = User(username='admin', password=hashed_password, is_admin=True)

    # Add the admin user to the database
    db.session.add(admin_user)
    db.session.commit()

    print("Admin user created with username 'admin' and password 'admin123'")
