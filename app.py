from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

DB_PATH = 'sensor_data.db'

def get_latest_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, temperature, light, rain_detected FROM sensor_data ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return rows[::-1]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    raw = get_latest_data()
    data = []
    for row in raw:
        data.append({
            'timestamp': row[0],
            'temperature': row[1],
            'light': row[2],
            'rain': bool(row[3])
        })
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
