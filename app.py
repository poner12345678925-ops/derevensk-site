import os
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Секретный ключ для защиты сессий

OWNER_EMAIL = "poner12345678925@gmail.com"

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            nickname TEXT,
            role TEXT DEFAULT 'player'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            type TEXT,
            target TEXT,
            text TEXT,
            video TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Деревенск РП | Форум</title>
    <style>
        :root {
            --bg-main: #0d0d0e;
            --bg-card: #141417;
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-red: #e53935;
            --text-main: #f1f1f5;
            --text-muted: #8e8e9e;
            --glass-bg: rgba(20, 20, 23, 0.85);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: sans-serif; }
        body { background-color: var(--bg-main); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }
        .glass { background: var(--glass-bg); backdrop-filter: blur(12px); border: 1px solid var(--border-color); }
        header { display: flex; justify-content: space-between; align-items: center; padding: 14px 40px; border-bottom: 1px solid var(--border-color); }
        .logo { font-size: 20px; font-weight: 800; color: #fff; text-transform: uppercase; }
        .logo span { color: var(--accent-red); }
        .main-container { display: flex; flex: 1; max-width: 1300px; width: 100%; margin: 0 auto; padding: 30px 20px; gap: 30px; }
        aside { width: 280px; display: flex; flex-direction: column; gap: 20px; }
        .menu-section { padding: 20px; border-radius: 12px; }
        .menu-btn { display: block; width: 100%; padding: 12px 14px; background: transparent; border: none; color: var(--text-muted); font-size: 14px; font-weight: 500; border-radius: 8px; cursor: pointer; text-align: left; margin-bottom: 6px; text-decoration: none; }
        .menu-btn:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }
        main { flex: 1; display: flex; flex-direction: column; gap: 24px; }
        .hero-card { border-radius: 14px; padding: 40px; min-height: 250px; background: url('https://i.postimg.cc/mD8zvhJ6/2026-10-18-113205.jpg') center/cover; position: relative; overflow: hidden; display: flex; align-items: flex-end; }
        .hero-overlay { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(13,13,14,0.2) 0%, rgba(13,13,14,0.95) 100%); }
        .hero-content { position: relative; z-index: 2; }
        .glass-btn { background: rgba(229, 57, 53, 0.3); border: 1px solid var(--accent-red); color: #fff; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
        .glass-btn:hover { background: rgba(229, 57, 53, 0.5); }
        .form-input, .form-select, .form-textarea { width: 100%; padding: 12px; background: rgba(255,255,255,0.04); border: 1px solid var(--border-color); border-radius: 8px; color: #fff; margin-bottom: 12px; }
        .complaint-card { padding: 16px; border-radius: 10px; margin-bottom: 12px; background: var(--bg-card); border: 1px solid var(--border-color); }
    </style>
</head>
<body>
    <header class="glass">
        <div class="logo"><span>Деревенск</span> РП</div>
        <div>
            {% if session.get('email') %}
                <span>👤 {{ session.get('nickname') }} (<b>{{ session.get('role').upper() }}</b>)</span> | 
                <a href="/logout" style="color: var(--accent-red); text-decoration: none;">Выйти</a>
            {% else %}
                <a href="/login_demo" class="glass-btn" style="text-decoration:none;">Войти как Владелец</a>
            {% endif %}
        </div>
    </header>

    <div class="main-container">
        <aside>
            <div class="menu-section glass">
                <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 10px; font-weight:700;">НАВИГАЦИЯ</div>
                <a href="/" class="menu-btn">🏠 Главная страница</a>
                <a href="/complaints" class="menu-btn">📜 Жалобы</a>
            </div>
            {% if session.get('role') == 'owner' %}
            <div class="menu-section glass" style="border-color: rgba(229,57,53,0.4);">
                <div style="font-size: 12px; color: var(--accent-red); margin-bottom: 10px; font-weight:700;">ПАНЕЛЬ ВЛАДЕЛЬЦА</div>
                <a href="/admin_panel" class="menu-btn">👑 Управление правами</a>
            </div>
            {% endif %}
        </aside>

        <main>
            {% if request.path == '/' %}
            <div class="hero-card glass">
                <div class="hero-overlay"></div>
                <div class="hero-content">
                    <h1 style="font-size: 32px; font-weight: 900; margin-bottom: 6px;">ДЕРЕВЕНСК РП</h1>
                    <p style="color: var(--text-muted);">Официальный защищенный портал проекта.</p>
                </div>
            </div>
            {% elif request.path == '/complaints' %}
            <div class="glass" style="padding: 24px; border-radius: 12px;">
                <h2 style="margin-bottom: 16px;">Подать жалобу</h2>
                <form action="/submit_complaint" method="POST" enctype="multipart/form-data">
                    <select name="type" class="form-select">
                        <option value="player">Жалоба на игрока</option>
                        <option value="admin">Жалоба на администратора (Только для Владельца)</option>
                    </select>
                    <input type="text" name="target" class="form-input" placeholder="Ник нарушителя" required>
                    <textarea name="text" class="form-textarea" placeholder="Суть нарушения..." required></textarea>
                    <input type="file" name="video" class="form-input" accept="video/*" required>
                    <button type="submit" class="glass-btn">Отправить</button>
                </form>

                <h2 style="margin-top: 30px; margin-bottom: 16px;">Список жалоб</h2>
                {% for c in complaints %}
                    {% if c[2] != 'admin' or session.get('role') == 'owner' %}
                    <div class="complaint-card">
                        <b>Жалоба на {{ c[3] }}</b> ({{ c[2] }})<br>
                        <span style="color: var(--text-muted);">От: {{ c[1] }} | Суть: {{ c[4] }}</span><br>
                        {% if c[5] %}
                        <video src="{{ c[5] }}" controls style="width: 200px; margin-top: 8px; border-radius: 6px;"></video>
                        {% endif %}
                    </div>
                    {% endif %}
                {% endfor %}
            </div>
            {% elif request.path == '/admin_panel' and session.get('role') == 'owner' %}
            <div class="glass" style="padding: 24px; border-radius: 12px;">
                <h2>Управление ролями</h2>
                <form action="/set_role" method="POST" style="margin-top: 15px;">
                    <input type="text" name="email" class="form-input" placeholder="Email игрока" required>
                    <select name="role" class="form-select">
                        <option value="admin">Администратор</option>
                        <option value="player">Игрок</option>
                    </select>
                    <button type="submit" class="glass-btn">Сохранить</button>
                </form>
            </div>
            {% endif %}
        </main>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/login_demo")
def login_demo():
    # Автоматический вход под твоей почтой владельца для проверки
    session['email'] = OWNER_EMAIL
    session['nickname'] = "Onqirs"
    session['role'] = "owner"
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/complaints")
def complaints():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, author, type, target, text, video, status FROM complaints ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, complaints=rows)

@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    if 'email' not in session:
        return redirect(url_for("login_demo"))
    
    author = session.get('nickname')
    ctype = request.form.get('type')
    target = request.form.get('target')
    text = request.form.get('text')
    
    video_file = request.files.get('video')
    video_path = ""
    if video_file:
        os.makedirs("static/uploads", exist_ok=True)
        video_path = f"/static/uploads/{video_file.filename}"
        video_file.save(os.path.join("static", "uploads", video_file.filename))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO complaints (author, type, target, text, video) VALUES (?, ?, ?, ?, ?)",
                   (author, ctype, target, text, video_path))
    conn.commit()
    conn.close()
    return redirect(url_for("complaints"))

@app.route("/set_role", methods=["POST"])
def set_role():
    if session.get('email') != OWNER_EMAIL:
        return "Доступ запрещен", 403
    
    target_email = request.form.get('email')
    new_role = request.form.get('role')
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = ? WHERE email = ?", (new_role, target_email))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
