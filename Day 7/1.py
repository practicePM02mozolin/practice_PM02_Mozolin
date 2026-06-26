"""
Веб-приложение для авторизации с разграничением ролей (админ/работник) и капчей
Кинотеатр - система управления заказами
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
    'host': 'localhost',
    'user': 'root',
    'password': '19852912',  # ВАШ ПАРОЛЬ ОТ MYSQL
    'database': 'cinima'
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
    """Создаёт базу данных и все таблицы"""
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
        
        # Таблица users (пользователи)
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
        
        # Таблица customers (клиенты)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id_customer INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Таблица 'customers' создана или уже существует")
        
        # Таблица orders (заказы)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id_order INT PRIMARY KEY AUTO_INCREMENT,
                id_customer INT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(10,2) DEFAULT 0,
                status VARCHAR(50) DEFAULT 'Новый',
                FOREIGN KEY (id_customer) REFERENCES customers(id_customer) ON DELETE SET NULL
            )
        """)
        print("✓ Таблица 'orders' создана или уже существует")
        
        # Добавляем тестовых клиентов, если их нет
        cursor.execute("SELECT COUNT(*) FROM customers")
        if cursor.fetchone()[0] == 0:
            customers_data = [
                ('Иван Петров', '+7-912-345-67-89', 'ivan@mail.ru'),
                ('Анна Сидорова', '+7-913-456-78-90', 'anna@mail.ru'),
                ('Сергей Иванов', '+7-914-567-89-01', 'sergey@mail.ru'),
                ('Елена Козлова', '+7-915-678-90-12', 'elena@mail.ru')
            ]
            for name, phone, email in customers_data:
                cursor.execute(
                    "INSERT INTO customers (name, phone, email) VALUES (%s, %s, %s)",
                    (name, phone, email)
                )
            print("✓ Добавлены тестовые клиенты")
        
        # Добавляем тестовые заказы, если их нет
        cursor.execute("SELECT COUNT(*) FROM orders")
        if cursor.fetchone()[0] == 0:
            orders_data = [
                (1, 1500.00, 'Новый'),
                (2, 2500.00, 'В обработке'),
                (1, 800.00, 'Готов'),
                (3, 3200.00, 'Выдан'),
                (2, 1200.00, 'Новый'),
                (4, 2100.00, 'В обработке')
            ]
            for id_customer, total_amount, status in orders_data:
                cursor.execute(
                    "INSERT INTO orders (id_customer, total_amount, status) VALUES (%s, %s, %s)",
                    (id_customer, total_amount, status)
                )
            print("✓ Добавлены тестовые заказы")
        
        # Создаём тестовых пользователей, если их нет
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
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


# ========== ПАНЕЛЬ РАБОТНИКА (ЗАКАЗЫ) ==========

@app.route('/worker/dashboard')
@login_required
def worker_dashboard():
    """Панель работника"""
    return render_template('worker/dashboard.html')


@app.route('/worker/orders')
@login_required
def worker_orders():
    """Просмотр всех заказов (для работника)"""
    conn = get_db_connection()
    if not conn:
        flash('Ошибка подключения к базе данных', 'danger')
        return redirect(url_for('worker_dashboard'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.id_order, o.order_date, o.total_amount, o.status,
               c.name as customer_name
        FROM orders o
        LEFT JOIN customers c ON o.id_customer = c.id_customer
        ORDER BY o.order_date DESC
    """)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('worker/orders.html', orders=orders)


@app.route('/worker/orders/update/<int:order_id>', methods=['GET', 'POST'])
@login_required
def worker_update_order(order_id):
    """Изменение статуса заказа"""
    if request.method == 'POST':
        new_status = request.form['status']
        
        conn = get_db_connection()
        if not conn:
            flash('Ошибка подключения к базе данных', 'danger')
            return redirect(url_for('worker_orders'))
        
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = %s WHERE id_order = %s", (new_status, order_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Статус заказа #{order_id} изменён на "{new_status}"', 'success')
        return redirect(url_for('worker_orders'))
    
    # GET запрос - показываем форму
    conn = get_db_connection()
    if not conn:
        flash('Ошибка подключения к базе данных', 'danger')
        return redirect(url_for('worker_dashboard'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.*, c.name as customer_name 
        FROM orders o
        LEFT JOIN customers c ON o.id_customer = c.id_customer
        WHERE o.id_order = %s
    """, (order_id,))
    order = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not order:
        flash('Заказ не найден', 'danger')
        return redirect(url_for('worker_orders'))
    
    statuses = ['Новый', 'В обработке', 'Готов', 'Выдан', 'Отменён']
    
    return render_template('worker/update_order.html', order=order, statuses=statuses)


# ========== HTML-ШАБЛОНЫ ==========

TEMPLATES = {
    'base.html': '''<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Кинотеатр - Управление{% endblock %}</title>
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
    <h2>Авторизация в системе кинотеатра</h2>
    <form method="POST">
        <div class="form-group">
            <label>Логин:</label>
            <input type="text" name="login" required placeholder="admin или worker">
        </div>
        <div class="form-group">
            <label>Пароль:</label>
            <input type="password" name="password" required placeholder="admin123 или worker123">
        </div>
        <div class="form-group">
            <label>🔐 Капча: сколько будет {{ num1 }} + {{ num2 }} ?</label>
            <input type="text" name="captcha" required placeholder="Введите число">
        </div>
        <button type="submit">Войти</button>
    </form>
    <p class="info">Тестовые пользователи: admin/admin123, worker/worker123</p>
</div>
{% endblock %}''',

    'admin/dashboard.html': '''{% extends "base.html" %}

{% block title %}Панель администратора{% endblock %}

{% block content %}
<h1>👑 Панель администратора</h1>
<p>Добро пожаловать, <strong>{{ session.login }}</strong>!</p>
<div class="menu">
    <ul>
        <li><a href="{{ url_for('admin_users') }}">📋 Управление пользователями</a></li>
        <li><a href="{{ url_for('worker_orders') }}">📦 Управление заказами</a></li>
        <li><a href="#">📊 Отчёты</a></li>
        <li><a href="{{ url_for('logout') }}">🚪 Выход</a></li>
    </ul>
</div>
{% endblock %}''',

    'admin/users.html': '''{% extends "base.html" %}

{% block title %}Управление пользователями{% endblock %}

{% block content %}
<h1>📋 Управление пользователями</h1>
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
<h1>➕ Добавление пользователя</h1>
<a href="{{ url_for('admin_users') }}" class="btn">← Назад</a>

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
            <option value="worker">👨‍💼 Работник</option>
            <option value="admin">👑 Администратор</option>
        </select>
    </div>
    <button type="submit">Создать</button>
</form>
{% endblock %}''',

    'worker/dashboard.html': '''{% extends "base.html" %}

{% block title %}Панель работника{% endblock %}

{% block content %}
<h1>👨‍💼 Панель работника</h1>
<p>Добро пожаловать, <strong>{{ session.login }}</strong>!</p>
<p>Ваша роль: {{ 'Администратор' if session.role == 'admin' else 'Работник' }}</p>

<div class="menu">
    <ul>
        <li><a href="{{ url_for('worker_orders') }}">📋 Просмотр заказов</a></li>
        <li><a href="{{ url_for('worker_orders') }}">✏️ Изменение статуса заказа</a></li>
        <li><a href="{{ url_for('logout') }}">🚪 Выход</a></li>
    </ul>
</div>
{% endblock %}''',

    'worker/orders.html': '''{% extends "base.html" %}

{% block title %}Просмотр заказов{% endblock %}

{% block content %}
<h1>📋 Просмотр заказов</h1>
<a href="{{ url_for('worker_dashboard') }}" class="btn">← Назад</a>

<a href="{% if not orders %}<p>Нет заказов для отображения.</p>{% endif %}

<tr>
    <thead>
        <tr>
            <th>ID</th>
            <th>Клиент</th>
            <th>Дата</th>
            <th>Сумма</th>
            <th>Статус</th>
            <th>Действие</th>
        </tr>
    </thead>
    <tbody>
        {% for order in orders %}
        <tr>
            <td>{{ order.id_order }}</td>
            <td>{{ order.customer_name or 'Нет данных' }}</td>
            <td>{{ order.order_date }}</td>
            <td>{{ order.total_amount }} руб.</td>
            <td style="color: 
                {% if order.status == 'Новый' %}blue
                {% elif order.status == 'В обработке' %}orange
                {% elif order.status == 'Готов' %}green
                {% elif order.status == 'Выдан' %}purple
                {% elif order.status == 'Отменён' %}red
                {% else %}black{% endif %}">
                {{ order.status }}
            </td>
            <td>
                <a href="{{ url_for('worker_update_order', order_id=order.id_order) }}" class="btn">✏️ Изменить статус</a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}''',

    'worker/update_order.html': '''{% extends "base.html" %}

{% block title %}Изменение статуса заказа{% endblock %}

{% block content %}
<h1>✏️ Изменение статуса заказа #{{ order.id_order }}</h1>

<div class="order-info">
    <p><strong>Клиент:</strong> {{ order.customer_name or 'Не указан' }}</p>
    <p><strong>Дата:</strong> {{ order.order_date }}</p>
    <p><strong>Сумма:</strong> {{ order.total_amount }} руб.</p>
    <p><strong>Текущий статус:</strong> 
        <span style="color: 
            {% if order.status == 'Новый' %}blue
            {% elif order.status == 'В обработке' %}orange
            {% elif order.status == 'Готов' %}green
            {% elif order.status == 'Выдан' %}purple
            {% elif order.status == 'Отменён' %}red
            {% else %}black{% endif %}">
            {{ order.status }}
        </span>
    </p>
</div>

<form method="POST" class="form">
    <div class="form-group">
        <label>Новый статус:</label>
        <select name="status" required>
            {% for status in statuses %}
                <option value="{{ status }}" {% if status == order.status %}selected{% endif %}>
                    {{ status }}
                </option>
            {% endfor %}
        </select>
    </div>
    <button type="submit">Сохранить</button>
    <a href="{{ url_for('worker_orders') }}" class="btn">Отмена</a>
</form>

<a href="{{ url_for('worker_dashboard') }}" class="btn">← Назад к панели</a>

<style>
.order-info {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
}
.order-info p {
    margin: 8px 0;
}
</style>
{% endblock %}'''
}

# ========== CSS ==========
CSS_CONTENT = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    border-radius: 15px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    padding: 30px;
}

.login-form {
    max-width: 400px;
    margin: 50px auto;
    padding: 30px;
    background: white;
    border-radius: 15px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.login-form h2 {
    text-align: center;
    margin-bottom: 25px;
    color: #333;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: bold;
    color: #555;
}

input, select {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
}

input:focus, select:focus {
    outline: none;
    border-color: #667eea;
}

button {
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    transform: translateY(-2px);
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    background: #667eea;
    color: white;
    text-decoration: none;
    border-radius: 8px;
    margin-right: 10px;
}

.btn:hover {
    background: #5a67d8;
}

.alert {
    padding: 12px 20px;
    margin-bottom: 20px;
    border-radius: 8px;
}

.alert-success {
    background: #d4edda;
    color: #155724;
    border-left: 4px solid #28a745;
}

.alert-danger {
    background: #f8d7da;
    color: #721c24;
    border-left: 4px solid #dc3545;
}

.alert-warning {
    background: #fff3cd;
    color: #856404;
    border-left: 4px solid #ffc107;
}

.alert-info {
    background: #d1ecf1;
    color: #0c5460;
    border-left: 4px solid #17a2b8;
}

.menu ul {
    list-style: none;
    padding: 0;
    margin-top: 20px;
}

.menu li {
    margin: 15px 0;
}

.menu a {
    display: block;
    padding: 15px 20px;
    background: #f8f9fa;
    border-radius: 10px;
    text-decoration: none;
    color: #333;
    font-size: 18px;
}

.menu a:hover {
    background: #667eea;
    color: white;
    transform: translateX(10px);
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background: #f8f9fa;
}

tr:hover {
    background: #f8f9fa;
}

.info {
    text-align: center;
    margin-top: 20px;
    color: #888;
    font-size: 12px;
}

h1 {
    color: #333;
    margin-bottom: 20px;
}
"""


# ========== ЗАПУСК ==========
if __name__ == '__main__':
    # Создаём папки для шаблонов и CSS
    os.makedirs('templates/admin', exist_ok=True)
    os.makedirs('templates/worker', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Создаём CSS файл
    with open('static/style.css', 'w', encoding='utf-8') as f:
        f.write(CSS_CONTENT)
    print("✓ Создан файл static/style.css")
    
    # Создаём HTML шаблоны
    for template_name, template_content in TEMPLATES.items():
        file_path = os.path.join('templates', template_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
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
