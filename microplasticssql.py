import sqlite3

# Connect to your database
conn = sqlite3.connect('microplastics.sqlite')

# Create a cursor
cursor = conn.cursor()

# OPTIONAL: See what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# --- NEW: Look inside the actual microplastic_data table ---
cursor.execute("SELECT * FROM microplastic_data;")
rows = cursor.fetchall()

# Print each row
print("\nContents of microplastic_data:")
for row in rows:
    print(row)

# Always close when done
conn.close()
