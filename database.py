import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # جدول المستخدمين: يوزر، رصيد، قسائم، إحالات، والـ IP للحماية
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, 
                  username TEXT, 
                  ip_address TEXT, 
                  balance REAL DEFAULT 0.0, 
                  coupons INTEGER DEFAULT 0, 
                  referrals INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def register_user(user_id, username, ip):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, ip_address) VALUES (?, ?, ?)", 
              (user_id, username, ip))
    conn.commit()
    conn.close()
