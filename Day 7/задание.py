"""
Веб-приложение для авторизации с разграничением ролей (админ/работник) и капчей
Кинотеатр - система управления
Запуск: python app.py
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
import bcrypt
from functools import wraps
import random
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey_2026_1234567890'

# ========== НАСТРОЙКИ ПОДКЛЮЧЕНИЯ К MYSQL (ИЗМЕНИТЕ ПОД СЕБЯ!) ==========
DB_CONFIG = {
    'host': 'localDB',   # ← попробуйте заменить на '127.0.0.1'
    'user': 'root',
    'password': '1234',        # ← ВАШ ПАРОЛЬ
    'database': 'cinema'
}

# ========== ФУНКЦИЯ ПОДКЛЮЧЕНИЯ К БД ==========
def get_db_connection():
    """Подключение к базе данных MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Ошибка подключения: {e}")
        return None


# ========== ДЕКОРАТОРЫ ДЛЯ ПРОВЕРКИ ДОСТУПА ==========

def login_required(f):
    """Требует авторизации"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Требует роли администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Доступ запрещён. Требуется роль администратора.', 'danger')
            return redirect(url_for('worker_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ========== ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ И ТАБЛИЦ ==========
def init_db():
    """Создаёт базу данных и таблицу users, если их нет"""
    # Подключаемся без базы данных
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Создаём базу данных
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"✓ База данных '{DB_CONFIG['database']}' создана или уже существует")
        
        # Переключаемся на базу
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Создаём таблицу users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id_user INT PRIMARY KEY AUTO_INCREMENT,
                login VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('admin', 'worker') DEFAULT 'worker',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Таблица 'users' создана или уже существует")
        
        # Проверяем, есть ли пользователи
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        # Создаём тестовых пользователей, если их нет
        if count == 0:
            users = [
                ('admin', 'admin123', 'admin'),
                ('worker', 'worker123', 'worker')
            ]
            for login, password, role in users:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute(
                    "INSERT INTO users (login, password_hash, role) VALUES (%s, %s, %s)",
                    (login, hashed.decode('utf-8'), role)
                )
                print(f"✓ Создан тестовый пользователь: {login} (пароль: {password}, роль: {role})")
            conn.commit()
        
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"✗ Ошибка инициализации БД: {e}")
        return False


# ========== СТРАНИЦЫ ==========

@app.route('/')
def index():
    """Главная страница"""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('worker_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа с капчей"""
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        captcha_user = request.form['captcha']

        # Проверка капчи
        if int(captcha_user) != session.get('captcha_result'):
            flash('Неверно введена капча', 'danger')
            return redirect(url_for('login'))

        # Поиск пользователя в БД
        conn = get_db_connection()
        if not conn:
            flash('Ошибка подключения к базе данных', 'danger')
            return redirect(url_for('login'))
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE login = %s", (login,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            stored_hash = user['password_hash']
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                session['user_id'] = user['id_user']
                session['login'] = user['login']
                session['role'] = user['role']
                flash(f'Добро пожаловать, {user["login"]}!', 'success')

                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('worker_dashboard'))
            else:
                flash('Неверный логин или пароль', 'danger')
        else:
            flash('Неверный логин или пароль', 'danger')

    # Генерация капчи
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    session['captcha_result'] = num1 + num2

    return render_template('login.html', num1=num1, num2=num2)


@app.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


# ========== ПАНЕЛЬ АДМИНИСТРАТОРА ==========

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Панель администратора"""
    return render_template('admin/dashboard.html')


@app.route('/admin/users')
@admin_required
def admin_users():
    """Управление пользователями"""
    conn = get_db_connection()
    if not conn:
        flash('Ошибка подключения к базе данных', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_user, login, role, created_at FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin/users.html', users=users)


@app.route('/admin/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Добавление нового пользователя"""
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        role = request.form['role']

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        if not conn:
            flash('Ошибка подключения к базе данных', 'danger')
            return redirect(url_for('admin_users'))
        
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (login, password_hash, role) VALUES (%s, %s, %s)",
                (login, hashed.decode('utf-8'), role)
            )
            conn.commit()
            flash(f'Пользователь {login} успешно создан', 'success')
        except Exception:
            flash('Ошибка: пользователь с таким логином уже существует', 'danger')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('admin_users'))

    return render_template('admin/add_user.html')


@app.route('/admin/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    """Удаление пользователя"""
    if user_id == session['user_id']:
        flash('Нельзя удалить самого себя', 'danger')
        return redirect(url_for('admin_users'))

    conn = get_db_connection()
    if not conn:
        flash('Ошибка подключения к базе данных', 'danger')
        return redirect(url_for('admin_users'))
    
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id_user = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Пользователь удалён', 'success')
    return redirect(url_for('admin_users'))


# ========== ПАНЕЛЬ РАБОТНИКА ==========

@app.route('/worker/dashboard')
@login_required
def worker_dashboard():
    """Панель работника"""
    return render_template('worker/dashboard.html')


# ========== HTML-ШАБЛОНЫ (ВСТРОЕННЫЕ) ==========

TEMPLATES = {
    'base.html': '''<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Моё приложение{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>''',

    'login.html': '''{% extends "base.html" %}

{% block title %}Вход в систему{% endblock %}

{% block content %}
<div class="login-form">
    <h2>Авторизация</h2>
    <form method="POST">
        <div class="form-group">
            <label>Логин:</label>
            <input type="text" name="login" required>
        </div>
        <div class="form-group">
            <label>Пароль:</label>
            <input type="password" name="password" required>
        </div>
        <div class="form-group">
            <label>Капча: сколько будет {{ num1 }} + {{ num2 }} ?</label>
            <input type="text" name="captcha" required>
        </div>
        <button type="submit">Войти</button>
    </form>
</div>
{% endblock %}''',

    'admin/dashboard.html': '''{% extends "base.html" %}

{% block title %}Панель администратора{% endblock %}

{% block content %}
<h1>Панель администратора</h1>
<p>Добро пожаловать, {{ session.login }}!</p>
<div class="menu">
    <ul>
        <li><a href="{{ url_for('admin_users') }}">📋 Управление пользователями</a></li>
        <li><a href="#">📦 Управление заказами</a></li>
        <li><a href="#">📊 Отчёты</a></li>
        <li><a href="{{ url_for('logout') }}">🚪 Выход</a></li>
    </ul>
</div>
{% endblock %}''',

    'admin/users.html': '''{% extends "base.html" %}

{% block title %}Управление пользователями{% endblock %}

{% block content %}
<h1>Управление пользователями</h1>
<a href="{{ url_for('add_user') }}" class="btn">➕ Добавить пользователя</a>
<a href="{{ url_for('admin_dashboard') }}" class="btn">← Назад</a>

<table>
    <thead>
        <tr><th>ID</th><th>Логин</th><th>Роль</th><th>Дата создания</th><th>Действия</th></tr>
    </thead>
    <tbody>
        {% for user in users %}
        <tr>
            <td>{{ user.id_user }}</td>
            <td>{{ user.login }}</td>
            <td>{{ 'Админ' if user.role == 'admin' else 'Работник' }}</td>
            <td>{{ user.created_at }}</td>
            <td><a href="{{ url_for('delete_user', user_id=user.id_user) }}" onclick="return confirm('Удалить пользователя?')">🗑️ Удалить</a></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}''',

    'admin/add_user.html': '''{% extends "base.html" %}

{% block title %}Добавление пользователя{% endblock %}

{% block content %}
<h1>Добавление пользователя</h1>
<a href="{{ url_for('admin_users') }}">← Назад</a>

<form method="POST" style="margin-top: 20px;">
    <div class="form-group">
        <label>Логин:</label>
        <input type="text" name="login" required>
    </div>
    <div class="form-group">
        <label>Пароль:</label>
        <input type="password" name="password" required>
    </div>
    <div class="form-group">
        <label>Роль:</label>
        <select name="role">
            <option value="worker">Работник</option>
            <option value="admin">Администратор</option>
        </select>
    </div>
    <button type="submit">Создать</button>
</form>
{% endblock %}''',

    'worker/dashboard.html': '''{% extends "base.html" %}

{% block title %}Панель работника{% endblock %}

{% block content %}
<h1>Панель работника</h1>
<p>Добро пожаловать, {{ session.login }}!</p>
<p>Ваша роль: {{ 'Администратор' if session.role == 'admin' else 'Работник' }}</p>
<div class="menu">
    <ul>
        <li><a href="#">🍕 Просмотр заказов</a></li>
        <li><a href="#">✏️ Изменение статуса заказа</a></li>
        <li><a href="{{ url_for('logout') }}">🚪 Выход</a></li>
    </ul>
</div>
{% endblock %}'''
}

# ========== CSS ==========
CSS_CONTENT = """body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: auto;
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

.login-form {
    width: 350px;
    margin: 50px auto;
    padding: 20px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

input, select, button {
    width: 100%;
    padding: 8px;
    margin: 5px 0;
    border: 1px solid #ddd;
    border-radius: 5px;
}

button {
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
}

button:hover {
    background-color: #0056b3;
}

.alert {
    padding: 10px;
    margin: 10px 0;
    border-radius: 5px;
}

.alert-success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.alert-danger {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.alert-warning {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeeba;
}

.menu ul {
    list-style: none;
    padding: 0;
}

.menu li {
    margin: 10px 0;
}

.menu a {
    text-decoration: none;
    color: #007bff;
    font-size: 18px;
}

.btn {
    display: inline-block;
    padding: 8px 15px;
    background: #007bff;
    color: white;
    text-decoration: none;
    border-radius: 5px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 10px;
    text-align: left;
    border: 1px solid #ddd;
}

th {
    background-color: #f4f4f4;
}
"""


# ========== ЗАПУСК ==========
if __name__ == '__main__':
    # Создаём папки для шаблонов и CSS
    os.makedirs('templates/admin', exist_ok=True)
    os.makedirs('templates/worker', exist_ok=True)  # ← ЭТА СТРОКА ИСПРАВЛЯЕТ ОШИБКУ
    os.makedirs('static', exist_ok=True)
    
    # Создаём CSS файл
    with open('static/style.css', 'w', encoding='utf-8') as f:
        f.write(CSS_CONTENT)
    print("✓ Создан файл static/style.css")
    
    # Создаём HTML шаблоны
    for template_name, template_content in TEMPLATES.items():
        # Создаём подпапки если нужно
        if '/' in template_name:
            subfolder = os.path.dirname(template_name)
            os.makedirs(f'templates/{subfolder}', exist_ok=True)
        
        file_path = os.path.join('templates', template_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print(f"✓ Создан шаблон templates/{template_name}")
    
    # Инициализируем базу данных
    print("\n=== ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ===")
    init_db()
    
    print("\n=== ЗАПУСК ПРИЛОЖЕНИЯ ===")
    print("Откройте в браузере: http://127.0.0.1:5000")
    print("Тестовые пользователи:")
    print("  admin / admin123 (администратор)")
    print("  worker / worker123 (работник)")
    print("\n")
    
    app.run(debug=True)
