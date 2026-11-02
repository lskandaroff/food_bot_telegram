import os, sqlite3, json
DB = os.path.join('e:/food_bot/backend', 'db.sqlite3')
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT id, title, image FROM restaurant_dish")
rows = cur.fetchall()
for row in rows:
    print(row)
conn.close()
