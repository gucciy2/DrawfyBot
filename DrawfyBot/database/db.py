import os
import sqlite3
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.db_path = 'drawfy.db'
        self.init_database()
    
    def init_database(self):
        """Создаем базу данных и таблицы если их нет"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                full_name TEXT,
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
                user_id INTEGER,
                title TEXT,
                description TEXT,
                filename TEXT,
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
                user_id INTEGER,
                drawing_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, drawing_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (drawing_id) REFERENCES drawings (id)
            )
        ''')
        
        # Таблица товаров магазина
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                price INTEGER,
                type TEXT
            )
        ''')
        
        # Заполняем товары если таблица пуста
        cursor.execute('SELECT COUNT(*) FROM shop_items')
        if cursor.fetchone()[0] == 0:
            items = [
                ('Кисть "Акварель"', 'Реалистичная акварельная кисть', 100, 'brush'),
                ('Кисть "Масло"', 'Текстурная масляная кисть', 150, 'brush'),
                ('Золотая рамка', 'Элегантная рамка для работ', 200, 'frame'),
                ('Фон "Космос"', 'Космический фон для рисунков', 300, 'background'),
                ('Аниме-стиль', 'Фильтр для аниме-стилизации', 250, 'filter')
            ]
            cursor.executemany(
                'INSERT INTO shop_items (name, description, price, type) VALUES (?, ?, ?, ?)',
                items
            )
        
        conn.commit()
        conn.close()
        print(f"✅ База данных создана: {self.db_path}")
    
    # ========== ПОЛЬЗОВАТЕЛИ ==========
    
    def get_user(self, telegram_id):
        """Получить пользователя по Telegram ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'telegram_id': user[1],
                'username': user[2],
                'full_name': user[3],
                'balance': user[4],
                'experience': user[5],
                'level': user[6],
                'created_at': user[7]
            }
        return None
    
    def create_user(self, telegram_id, username, full_name):
        """Создать нового пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (telegram_id, username, full_name) 
                VALUES (?, ?, ?)
            ''', (telegram_id, username, full_name))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            return self.get_user(telegram_id)
        except sqlite3.IntegrityError:
            conn.close()
            return self.get_user(telegram_id)  # Уже существует
    
    # ========== РИСУНКИ ==========
    
    def add_drawing(self, user_id, title, description, filename):
        """Добавить рисунок"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO drawings (user_id, title, description, filename) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, description, filename))
        
        conn.commit()
        drawing_id = cursor.lastrowid
        conn.close()
        
        return drawing_id
    
    def get_drawings(self, limit=20):
        """Получить последние рисунки"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, u.username, u.full_name 
            FROM drawings d
            LEFT JOIN users u ON d.user_id = u.id
            ORDER BY d.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        drawings = []
        for row in cursor.fetchall():
            drawings.append(dict(row))
        
        conn.close()
        return drawings
    
    def get_user_drawings(self, user_id):
        """Получить рисунки пользователя"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM drawings 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        drawings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return drawings
    
    # ========== ЛАЙКИ ==========
    
    def add_like(self, user_id, drawing_id):
        """Поставить лайк"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Добавляем лайк
            cursor.execute('''
                INSERT INTO likes (user_id, drawing_id) VALUES (?, ?)
            ''', (user_id, drawing_id))
            
            # Увеличиваем счетчик лайков у рисунка
            cursor.execute('''
                UPDATE drawings SET likes = likes + 1 WHERE id = ?
            ''', (drawing_id,))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False  # Уже лайкал
    
    # ========== МАГАЗИН ==========
    
    def get_shop_items(self):
        """Получить товары магазина"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM shop_items ORDER BY price')
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    def buy_item(self, user_id, item_id):
        """Купить товар"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Получаем цену товара
        cursor.execute('SELECT price FROM shop_items WHERE id = ?', (item_id,))
        item = cursor.fetchone()
        
        if not item:
            conn.close()
            return False
        
        price = item[0]
        
        # Проверяем баланс пользователя
        cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user or user[0] < price:
            conn.close()
            return False
        
        # Списываем деньги и добавляем покупку
        cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (price, user_id))
        
        # Здесь можно добавить запись о покупке в отдельную таблицу
        
        conn.commit()
        conn.close()
        return True
    
    # ========== СТАТИСТИКА ==========
    
    def get_stats(self):
        """Получить статистику"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM drawings')
        total_drawings = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(likes) FROM drawings')
        total_likes = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_drawings': total_drawings,
            'total_likes': total_likes
        }

# Создаем глобальный объект базы данных
db = Database()

# Для быстрого тестирования
if __name__ == '__main__':
    print("🔧 Тестируем базу данных...")
    
    # Создаем тестового пользователя
    user = db.create_user(123456789, 'test_user', 'Тестовый Пользователь')
    print(f"👤 Создан пользователь: {user}")
    
    # Получаем товары магазина
    items = db.get_shop_items()
    print(f"🛒 Товаров в магазине: {len(items)}")
    
    # Получаем статистику
    stats = db.get_stats()
    print(f"📊 Статистика: {stats}")
    
    print("✅ Тест завершен!")