import sqlite3

conn = sqlite3.connect("database/school.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS attendance")

conn.commit()
conn.close()

print("Attendance table deleted successfully.")