import os
import json
import base64
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Настройки
app.config['UPLOAD_FOLDER'] = 'static/drawings'
app.config['DATABASE'] = 'drawfy.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Создаем папки если их нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/avatars', exist_ok=True)

# ==================== ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ====================

def init_database():
    """Создаем базу данных и таблицы если их нет"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Таблица пользователей (из Telegram)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            balance INTEGER DEFAULT 100,
            experience INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица рисунков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drawings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            filename TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Таблица лайков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            drawing_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, drawing_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (drawing_id) REFERENCES drawings (id)
        )
    ''')
    
    # Таблица комментариев
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            drawing_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (drawing_id) REFERENCES drawings (id)
        )
    ''')
    
    # Таблица товаров магазина
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            type TEXT,
            image_url TEXT
        )
    ''')
    
    # Таблица покупок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (item_id) REFERENCES shop_items (id)
        )
    ''')
    
    # Добавляем тестовые товары если таблица пуста
    cursor.execute('SELECT COUNT(*) FROM shop_items')
    if cursor.fetchone()[0] == 0:
        test_items = [
            ('Кисть "Акварель"', 'Реалистичная акварельная кисть', 100, 'brush', '🖌️'),
            ('Кисть "Масло"', 'Текстурная масляная кисть', 150, 'brush', '🎨'),
            ('Золотая рамка', 'Элегантная рамка для работ', 200, 'frame', '🖼️'),
            ('Фон "Космос"', 'Космический фон для рисунков', 300, 'background', '🌌'),
            ('Аниме-стиль', 'Фильтр для аниме-стилизации', 250, 'filter', '🌸'),
            ('Профессиональный набор', '10 премиум кистей + 5 фонов', 1000, 'bundle', '🎁')
        ]
        cursor.executemany(
            'INSERT INTO shop_items (name, description, price, type, image_url) VALUES (?, ?, ?, ?, ?)',
            test_items
        )
    
    # Добавляем тестовых пользователей если нужно
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        test_users = [
            (123456789, 'art_lover', 'Анна', 'Художникова'),
            (987654321, 'creative_soul', 'Максим', 'Творец'),
            (555555555, 'digital_artist', 'Ольга', 'Арт')
        ]
        cursor.executemany(
            'INSERT INTO users (telegram_id, username, first_name, last_name, balance) VALUES (?, ?, ?, ?, ?)',
            [(id, user, first, last, 500) for id, user, first, last in test_users]
        )
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

# Инициализируем БД при запуске
init_database()

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_db_connection():
    """Создает соединение с базой данных"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def get_or_create_user(telegram_id, username=None, first_name=None, last_name=None):
    """Получить или создать пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute('''
            INSERT INTO users (telegram_id, username, first_name, last_name) 
            VALUES (?, ?, ?, ?)
        ''', (telegram_id, username, first_name, last_name))
        conn.commit()
        user_id = cursor.lastrowid
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
    
    conn.close()
    return dict(user) if user else None

# ==================== СТРАНИЦЫ WEB APP ====================

@app.route('/')
def index():
    """Главная страница Web App"""
    return render_template('index.html')

@app.route('/draw')
def draw_page():
    """Страница рисования"""
    return render_template('draw.html')

@app.route('/gallery')
def gallery_page():
    """Галерея работ"""
    return render_template('gallery.html')

@app.route('/shop')
def shop_page():
    """Магазин"""
    return render_template('shop.html')

@app.route('/profile')
def profile_page():
    """Профиль пользователя"""
    return render_template('profile.html')

# ==================== API ДЛЯ TELEGRAM ====================

@app.route('/api/telegram-auth', methods=['POST'])
def telegram_auth():
    """Аутентификация пользователя из Telegram"""
    try:
        data = request.json
        init_data = data.get('initData')
        
        # В реальном проекте здесь нужно проверять подпись от Telegram
        # Для тестирования принимаем данные как есть
        user_data = data.get('user', {})
        
        telegram_id = user_data.get('id')
        username = user_data.get('username')
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        
        if not telegram_id:
            return jsonify({'error': 'Неверные данные Telegram'}), 400
        
        # Получаем или создаем пользователя
        user = get_or_create_user(telegram_id, username, first_name, last_name)
        
        return jsonify({
            'success': True,
            'user': user,
            'token': f"user_{telegram_id}"  # Простой токен для теста
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== API ДЛЯ РИСУНКОВ ====================

@app.route('/api/drawings', methods=['GET'])
def get_drawings():
    """Получить все рисунки"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Получаем рисунки с информацией о пользователях
        cursor.execute('''
            SELECT 
                d.*,
                u.username,
                u.first_name,
                u.last_name,
                (SELECT COUNT(*) FROM likes WHERE drawing_id = d.id) as like_count,
                (SELECT COUNT(*) FROM comments WHERE drawing_id = d.id) as comment_count
            FROM drawings d
            JOIN users u ON d.user_id = u.id
            ORDER BY d.created_at DESC
            LIMIT 100
        ''')
        
        drawings = []
        for row in cursor.fetchall():
            drawing = dict(row)
            # Формируем URL к изображению
            drawing['image_url'] = f"/static/drawings/{drawing['filename']}"
            # Формируем имя автора
            drawing['author_name'] = f"{drawing['first_name']} {drawing['last_name'] or ''}".strip()
            if drawing['username']:
                drawing['author_name'] += f" (@{drawing['username']})"
            
            drawings.append(drawing)
        
        conn.close()
        return jsonify({'success': True, 'drawings': drawings})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/drawings/upload', methods=['POST'])
def upload_drawing():
    """Загрузить новый рисунок"""
    try:
        data = request.json
        
        # Проверяем токен (в реальном проекте нужно проверять JWT)
        user_token = data.get('token')
        if not user_token or not user_token.startswith('user_'):
            return jsonify({'error': 'Неавторизован'}), 401
        
        telegram_id = int(user_token.replace('user_', ''))
        user = get_or_create_user(telegram_id)
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        title = data.get('title', 'Без названия')
        description = data.get('description', '')
        image_data = data.get('image')  # base64
        
        if not image_data:
            return jsonify({'error': 'Нет изображения'}), 400
        
        # Декодируем base64
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Сохраняем файл
        filename = f"drawing_{user['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(image_data))
        
        # Сохраняем в базу данных
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO drawings (user_id, title, description, filename) 
            VALUES (?, ?, ?, ?)
        ''', (user['id'], title, description, filename))
        
        drawing_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Начисляем опыт за загрузку
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET experience = experience + 10, balance = balance + 10 WHERE id = ?', 
                      (user['id'],))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Рисунок успешно сохранен!',
            'drawing_id': drawing_id,
            'image_url': f"/static/drawings/{filename}",
            'reward': {'experience': 10, 'coins': 10}
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/drawings/<int:drawing_id>/like', methods=['POST'])
def like_drawing(drawing_id):
    """Поставить лайк рисунку"""
    try:
        data = request.json
        user_token = data.get('token')
        
        if not user_token or not user_token.startswith('user_'):
            return jsonify({'error': 'Неавторизован'}), 401
        
        telegram_id = int(user_token.replace('user_', ''))
        user = get_or_create_user(telegram_id)
        
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Проверяем, не лайкал ли уже
        cursor.execute('SELECT id FROM likes WHERE user_id = ? AND drawing_id = ?', 
                      (user['id'], drawing_id))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Вы уже лайкнули этот рисунок'}), 400
        
        # Добавляем лайк
        cursor.execute('INSERT INTO likes (user_id, drawing_id) VALUES (?, ?)', 
                      (user['id'], drawing_id))
        cursor.execute('UPDATE drawings SET likes = likes + 1 WHERE id = ?', 
                      (drawing_id,))
        
        # Начисляем опыт автору рисунка
        cursor.execute('SELECT user_id FROM drawings WHERE id = ?', (drawing_id,))
        author_row = cursor.fetchone()
        if author_row:
            author_id = author_row['user_id']
            cursor.execute('UPDATE users SET experience = experience + 1, balance = balance + 1 WHERE id = ?', 
                          (author_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Лайк добавлен!',
            'reward': {'experience': 1, 'coins': 1}
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== API ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ====================

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Получить профиль пользователя"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Основная информация
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        user_data = dict(user)
        
        # Статистика
        cursor.execute('SELECT COUNT(*) FROM drawings WHERE user_id = ?', (user_id,))
        drawings_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(likes) FROM drawings WHERE user_id = ?', (user_id,))
        total_likes = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT COUNT(DISTINCT drawing_id) 
            FROM likes 
            WHERE drawing_id IN (SELECT id FROM drawings WHERE user_id = ?)
        ''', (user_id,))
        unique_likers = cursor.fetchone()[0] or 0
        
        # Последние работы
        cursor.execute('''
            SELECT * FROM drawings 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 5
        ''', (user_id,))
        
        recent_drawings = []
        for row in cursor.fetchall():
            drawing = dict(row)
            drawing['image_url'] = f"/static/drawings/{drawing['filename']}"
            recent_drawings.append(drawing)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'user': user_data,
            'stats': {
                'drawings_count': drawings_count,
                'total_likes': total_likes,
                'unique_likers': unique_likers,
                'level': user_data['level'],
                'experience': user_data['experience'],
                'balance': user_data['balance']
            },
            'recent_drawings': recent_drawings
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== API ДЛЯ МАГАЗИНА ====================

@app.route('/api/shop/items', methods=['GET'])
def get_shop_items():
    """Получить товары магазина"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM shop_items ORDER BY price')
        items = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return jsonify({'success': True, 'items': items})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/shop/buy', methods=['POST'])
def buy_item():
    """Купить товар"""
    try:
        data = request.json
        user_token = data.get('token')
        item_id = data.get('item_id')
        
        if not user_token or not user_token.startswith('user_'):
            return jsonify({'error': 'Неавторизован'}), 401
        
        telegram_id = int(user_token.replace('user_', ''))
        user = get_or_create_user(telegram_id)
        
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Получаем информацию о товаре
        cursor.execute('SELECT * FROM shop_items WHERE id = ?', (item_id,))
        item = cursor.fetchone()
        
        if not item:
            conn.close()
            return jsonify({'error': 'Товар не найден'}), 404
        
        item_data = dict(item)
        
        # Проверяем баланс
        if user['balance'] < item_data['price']:
            conn.close()
            return jsonify({'error': 'Недостаточно монет'}), 400
        
        # Проверяем, не куплен ли уже
        cursor.execute('SELECT id FROM purchases WHERE user_id = ? AND item_id = ?', 
                      (user['id'], item_id))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Уже куплено'}), 400
        
        # Списываем деньги и добавляем покупку
        cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', 
                      (item_data['price'], user['id']))
        cursor.execute('INSERT INTO purchases (user_id, item_id) VALUES (?, ?)', 
                      (user['id'], item_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Товар "{item_data["name"]}" куплен!',
            'new_balance': user['balance'] - item_data['price']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== СТАТИЧЕСКИЕ ФАЙЛЫ ====================

@app.route('/static/drawings/<filename>')
def serve_drawing(filename):
    """Отдать рисунок"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/static/<path:path>')
def serve_static(path):
    """Отдать статические файлы"""
    return send_from_directory('static', path)

# ==================== ЗАПУСК СЕРВЕРА ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Drawfy Server запускается...")
    print(f"📡 API доступен на: http://localhost:{port}")
    print(f"🌐 Web App: http://localhost:{port}/")
    print(f"💾 База данных: {app.config['DATABASE']}")
    print(f"📁 Загрузки: {app.config['UPLOAD_FOLDER']}")
    print("\n📌 Доступные эндпоинты:")
    print(f"  GET  /api/drawings          - Все рисунки")
    print(f"  POST /api/drawings/upload   - Загрузить рисунок")
    print(f"  POST /api/telegram-auth     - Авторизация Telegram")
    print(f"  GET  /api/users/<id>        - Профиль пользователя")
    print(f"  GET  /api/shop/items        - Товары магазина")
    print("\n✨ Сервер готов! Нажми Ctrl+C чтобы остановить")
    
    app.run(host='0.0.0.0', port=port, debug=True)