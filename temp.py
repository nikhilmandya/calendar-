from app import db
db.drop_all()  # Drops all tables
db.create_all()  # Recreates tables with the updated schema
exit()