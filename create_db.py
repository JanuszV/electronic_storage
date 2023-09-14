import sqlite3

# Connect to the database or create it if it doesn't exist
conn = sqlite3.connect("mydb.db")

# Create a cursor
cursor = conn.cursor()

# Create the "contacts" table
cursor.execute('''CREATE TABLE IF NOT EXISTS electronics
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   type TEXT NOT NULL,
                   part_number TEXT,
                   value TEXT,
                   quantity INTEGER CHECK(quantity >= 0) NOT NULL,
                   note TEXT)''')

# Commit changes and close the connection
conn.commit()
conn.close()