import serial
import sqlite3
from datetime import datetime

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Connect to SQLite database
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    temperature REAL,
    light INTEGER,
    rain_detected INTEGER
)
''')
conn.commit()

print("Listening to Arduino via Serial...")

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            try:
                temperature, light, rain = line.split(',')
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "INSERT INTO sensor_data (timestamp, temperature, light, rain_detected) VALUES (?, ?, ?, ?)",
                    (timestamp, float(temperature), int(light), int(rain))
                )
                conn.commit()
                print(f"Saved: {timestamp} | Temp: {temperature} *C | Light: {light} | Rain: {rain}")
            except Exception as e:
                print("Parse error:", line, e)
except KeyboardInterrupt:
    print("Program interrupted by user.")
finally:
    ser.close()
    conn.close()   
