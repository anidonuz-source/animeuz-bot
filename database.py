import pymysql

# ================= MySQL bilan ulanish =================
try:
    db = pymysql.connect(
        host="127.0.0.1",  # localhost o'rniga 127.0.0.1 sinab ko'ring
        user="root",        # XAMPP default
        password="",        # XAMPP default bo'sh
        database="anime_bot",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
except Exception as e:
    print("❌ Ulanishda xatolik:", e)
    exit()

cursor = db.cursor()

# ================= User qo'shish =================
def add_user(user_id, username=None):
    sql = "INSERT IGNORE INTO users (user_id, username) VALUES (%s, %s)"
    cursor.execute(sql, (user_id, username))
    db.commit()

def get_users_count():
    cursor.execute("SELECT COUNT(*) AS cnt FROM users")
    return cursor.fetchone()['cnt']

def get_users_count_days(days):
    sql = f"SELECT COUNT(*) AS cnt FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)"
    cursor.execute(sql, (days,))
    return cursor.fetchone()['cnt']

def get_users():
    cursor.execute("SELECT user_id FROM users")
    return [(u['user_id'],) for u in cursor.fetchall()]

# ================= Anime =================
def save_anime(title, genre, votes, year):
    sql = "INSERT INTO anime (title, genre, votes_info, year) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (title, genre, votes, year))
    db.commit()

def get_anime_count():
    cursor.execute("SELECT COUNT(*) AS cnt FROM anime")
    return cursor.fetchone()['cnt']

def get_anime_by_id(anime_id):
    cursor.execute("SELECT * FROM anime WHERE id=%s", (anime_id,))
    return cursor.fetchone()

def get_anime_by_name(name):
    cursor.execute("SELECT * FROM anime WHERE title=%s", (name,))
    return cursor.fetchone()

# ================= Qismlar =================
def get_episodes_count(anime_id):
    cursor.execute("SELECT COUNT(*) AS cnt FROM episodes WHERE anime_id=%s", (anime_id,))
    return cursor.fetchone()['cnt']

def get_episode(anime_id, episode_number):
    cursor.execute("SELECT * FROM episodes WHERE anime_id=%s AND episode_number=%s", (anime_id, episode_number))
    return cursor.fetchone()

def update_episode_media(anime_id, episode_number, media):
    sql = "UPDATE episodes SET media=%s WHERE anime_id=%s AND episode_number=%s"
    cursor.execute(sql, (media, anime_id, episode_number))
    db.commit()

# ================= Bot admin tekshiruv =================
def bot_is_admin(channel_username):
    # Bu joyni sizning bot API bilan tekshirish kerak
    return True

# ================= Majburiy kanallar =================
def add_mandatory_channel(username):
    sql = "INSERT IGNORE INTO mandatory_channels (username) VALUES (%s)"
    cursor.execute(sql, (username,))
    db.commit()

def get_mandatory_channels():
    cursor.execute("SELECT * FROM mandatory_channels")
    return cursor.fetchall()

def delete_mandatory_channel(ch_id):
    cursor.execute("DELETE FROM mandatory_channels WHERE id=%s", (ch_id,))
    db.commit()

# ================= Sozlamalar =================
def get_settings():
    cursor.execute("SELECT * FROM settings LIMIT 1")
    s = cursor.fetchone()
    if not s:
        cursor.execute("INSERT INTO settings () VALUES ()")
        db.commit()
        cursor.execute("SELECT * FROM settings LIMIT 1")
        s = cursor.fetchone()
    return s

def update_setting(field, value):
    cursor.execute(f"UPDATE settings SET {field}=%s WHERE id=1", (value,))
    db.commit()