import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE stories ADD COLUMN file_path TEXT;")
except sqlite3.OperationalError:
    pass # column might exist

try:
    cursor.execute("ALTER TABLE stories ADD COLUMN is_upload INTEGER DEFAULT 0;")
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE stories ADD COLUMN extracted_text TEXT;")
except sqlite3.OperationalError:
    pass

conn.commit()
conn.close()
print("Database schema updated.")
