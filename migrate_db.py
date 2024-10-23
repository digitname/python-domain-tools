import sqlite3

def migrate_db():
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    
    # Check if email column exists
    c.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'email' not in columns:
        print("Adding email column to users table...")
        c.execute("ALTER TABLE users ADD COLUMN email TEXT UNIQUE")
        conn.commit()
        print("Email column added successfully.")
    else:
        print("Email column already exists in users table.")
    
    conn.close()

if __name__ == "__main__":
    migrate_db()
