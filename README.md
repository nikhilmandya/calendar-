
# Flask Application with PostgreSQL and Docker

This project is a Flask-based web application using PostgreSQL as the database. The application allows admin users to manage events and users, and regular users can view and download their events.

---

## Prerequisites

1. **Docker** and **Docker Compose**
   - [Docker Installation Guide](https://docs.docker.com/get-docker/)

2. **Python 3.7+** and `pip`
   - [Python Installation Guide](https://www.python.org/downloads/)

3. **Virtualenv** (optional, for Python environment isolation)
   ```bash
   pip install virtualenv
   ```

---

## Features

- Admin panel for creating users and events.
- Regular users can view their events.
- Export events as `.ics` for calendar applications or `.pdf` for reports.
- PostgreSQL as the database managed through Docker.

---

## Installation and Setup

### Step 1: Clone the Project

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

---

### Step 2: Run PostgreSQL in Docker

1. Start a PostgreSQL container:
   ```bash
   docker run --name postgres-db      -e POSTGRES_USER=calendar_user      -e POSTGRES_PASSWORD=your_password      -e POSTGRES_DB=calendar_app      -p 5432:5432      -d postgres
   ```

2. Verify the container is running:
   ```bash
   docker ps
   ```

---

### Step 3: Set Up the Flask Application

1. **Create a Virtual Environment** (optional):
   ```bash
   virtualenv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Update Database Configuration**:
   In `app.py`, configure the PostgreSQL database URI:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://calendar_user:your_password@localhost:5432/calendar_app'
   ```

   Replace `your_password` with the password set in Step 2.

---

### Step 4: Initialize the Database

1. **Create Tables**:
   Run the following commands in Python shell to create tables:
   ```bash
   python
   ```

   Inside the Python shell:
   ```python
   from app import db
   db.create_all()
   exit()
   ```

2. **Add an Initial Admin User**:
   Run the Python shell again:
   ```bash
   python
   ```

   Add the admin user:
   ```python
   from app import db, User
   from werkzeug.security import generate_password_hash

   admin_user = User(username='admin', password=generate_password_hash('admin_password'), is_admin=True)
   db.session.add(admin_user)
   db.session.commit()
   exit()
   ```

---

### Step 5: Run the Flask Application

Start the Flask development server:
```bash
python app.py
```

Access the application at [http://localhost:5000](http://localhost:5000).

---

## Managing the PostgreSQL Container

### Stop the Container
```bash
docker stop postgres-db
```

### Restart the Container
```bash
docker start postgres-db
```

### Remove the Container
```bash
docker rm -f postgres-db
```

---

## Additional Notes

- **Database Backup**:
  ```bash
  docker exec postgres-db pg_dump -U calendar_user calendar_app > backup.sql
  ```

- **Restore Database**:
  ```bash
  docker exec -i postgres-db psql -U calendar_user -d calendar_app < backup.sql
  ```

- **Environment Variables**:
  Store sensitive information like database credentials in environment variables or a `.env` file.

---

Let me know if you need further assistance!
