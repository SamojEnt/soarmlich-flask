<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mysecret")

# Database: use cloud if available, fallback to local sqlite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Route to initialize database and create default user
@app.route('/initdb')
def initdb():
    db.create_all()
    
    # Create default admin user only if not exists
    if not User.query.filter_by(username="admin").first():
        hashed_password = generate_password_hash("admin123")
        admin_user = User(username="admin", password_hash=hashed_password)
        db.session.add(admin_user)
        db.session.commit()
        return "Database initialized with default admin user (admin / admin123)"
    
    return "Database already initialized."

# Login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

# Dashboard after login
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['user'])

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Main
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
=======
from flask import Flask, render_template, request, redirect, url_for, session, Response
import sensor_readings
import cv2

app = Flask(__name__)
app.secret_key = 'secret_key_123'

# RTSP camera URL
rtsp_url = 'rtsp://admin:Vikash%401422@192.168.0.101:554/cam/realmonitor?channel=1&subtype=0'
camera = cv2.VideoCapture(rtsp_url)

def gen_frames():
    global camera
    while True:
        if not camera.isOpened():
            camera.open(rtsp_url)

        success, frame = camera.read()
        if not success:
            camera.release()
            camera = cv2.VideoCapture(rtsp_url)
            continue

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/site_status')
def site_status():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('site_status.html')

@app.route('/map_view')
def map_view():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('map_view.html')

@app.route('/camera_status')
def camera_status():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    sensors = sensor_readings.get_sensor_list()
    return render_template('camera_status.html', sensors=sensors)

@app.route('/video_feed')
def video_feed():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/sensor_data/<sensor_name>')
def sensor_data(sensor_name):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    raw_value = sensor_readings.read_sensor(sensor_name)
    return {'sensor': sensor_name, 'value': raw_value}

@app.route('/regular_report')
def regular_report():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('regular_report.html')

@app.route('/industrial_report')
def industrial_report():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('industrial_report.html')

@app.route('/calibration')
def calibration():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('calibration.html')

@app.route('/alarm')
def alarm():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('alarm.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
>>>>>>> 659d7bb (Initial comit from Raspberry Pi)
