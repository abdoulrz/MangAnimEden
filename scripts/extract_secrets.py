import sqlite3
import os

db_path = 'db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute('SELECT client_id, secret FROM socialaccount_socialapp WHERE provider="google"')
        row = cur.fetchone()
        if row:
            print(f"CLIENT_ID={row[0]}")
            print(f"SECRET={row[1]}")
        else:
            print("No Google SocialApp found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("db.sqlite3 not found.")
