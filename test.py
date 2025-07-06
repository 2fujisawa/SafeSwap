import sqlite3

# Connect to your database file
conn = sqlite3.connect('microplastics.sqlite')
cursor = conn.cursor()

# Show all tables
print("Tables in database:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print("-", table[0])

# Show schema of scan_history table
print("\nSchema of scan_history table:")
cursor.execute("PRAGMA table_info(scan_history);")
columns = cursor.fetchall()
for col in columns:
    print(f"{col[1]} ({col[2]})")

# Show 5 rows from scan_history
print("\nRecent scans:")
cursor.execute("SELECT * FROM scan_history ORDER BY time_scanned DESC LIMIT 5;")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()