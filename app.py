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
