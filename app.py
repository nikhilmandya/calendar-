from flask import Flask, render_template, redirect, request, url_for, session, flash, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ics import Calendar, Event as IcsEvent
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Flask app setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# PostgreSQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://calendar_user:your_password@localhost:5432/calendar_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('events', lazy=True))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Timestamp of creation



# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if not user.is_admin:
            flash('Access denied!', 'danger')
            return redirect(url_for('home'))
        users = User.query.all()
        events = Event.query.all()
        return render_template('admin_dashboard.html', users=users, events=events)
    return redirect(url_for('login'))


@app.route('/admin/create_user', methods=['POST'])
def create_user():
    if 'user_id' in session and User.query.get(session['user_id']).is_admin:
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/create_event', methods=['POST'])
def create_event():
    title = request.form['title']
    description = request.form['description']
    user_id = request.form['user_id']
    start_date = request.form['start_date']
    start_time = request.form['start_time']
    end_date = request.form['end_date']
    end_time = request.form['end_time']

    start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
    end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")

    new_event = Event(
        title=title,
        description=description,
        user_id=user_id,
        start_time=start_datetime,
        end_time=end_datetime
    )
    db.session.add(new_event)
    db.session.commit()

    flash('Event created successfully!', 'success')
    return redirect('/admin')


@app.route('/user')
def user_dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.is_admin:
            flash('Access denied!', 'danger')
            return redirect(url_for('admin_dashboard'))
        events = Event.query.filter_by(user_id=user.id).all()
        return render_template('user_dashboard.html', events=events)
    return redirect(url_for('login'))


@app.route('/admin/download_pdf', methods=['POST'])
def download_pdf():
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

    events = Event.query.filter(Event.start_time >= start_date_obj, Event.end_time <= end_date_obj).all()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Events Report")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(30, 750, "Events Report")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(30, 730, f"Date Range: {start_date} to {end_date}")
    pdf.drawString(30, 710, f"Total Events: {len(events)}")

    y_position = 690
    pdf.setFont("Helvetica", 10)
    for event in events:
        pdf.drawString(30, y_position, f"ID: {event.id}, Title: {event.title}, User: {event.user.username}")
        pdf.drawString(30, y_position - 15, f"Description: {event.description}")
        pdf.drawString(30, y_position - 30, f"Start: {event.start_time}, End: {event.end_time}")
        y_position -= 60
        if y_position < 50:
            pdf.showPage()
            y_position = 750

    pdf.save()
    buffer.seek(0)

    response = Response(buffer.getvalue(), mimetype="application/pdf")
    response.headers['Content-Disposition'] = 'attachment; filename=events_report.pdf'
    return response


@app.route('/user/download_event/<int:event_id>', methods=['GET'])
def download_event_ics(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found!', 'danger')
        return redirect('/user')

    c = Calendar()
    e = IcsEvent()
    e.name = event.title
    e.description = event.description
    e.begin = event.start_time.strftime("%Y-%m-%d %H:%M:%S")
    e.end = event.end_time.strftime("%Y-%m-%d %H:%M:%S")
    c.events.add(e)

    response = Response(str(c), mimetype="text/calendar")
    response.headers['Content-Disposition'] = f'attachment; filename=event_{event.id}.ics'
    return response


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
