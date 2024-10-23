import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    
    # Create domains table
    c.execute('''CREATE TABLE IF NOT EXISTS domains
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, domain TEXT UNIQUE, category TEXT)''')
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')
    
    conn.commit()
    conn.close()

def create_admin_user(username, password):
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    
    hashed_password = generate_password_hash(password)
    c.execute("INSERT OR REPLACE INTO users (username, password) VALUES (?, ?)",
              (username, hashed_password))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    
    admin_username = input("Enter admin username: ")
    admin_password = input("Enter admin password: ")
    create_admin_user(admin_username, admin_password)
    
    print("Database initialized and admin user created successfully.")
