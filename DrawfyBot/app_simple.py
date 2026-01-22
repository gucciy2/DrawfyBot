import os
from flask import Flask, render_template, jsonify, request
import json

app = Flask(__name__)

# Создаем папки если их нет
os.makedirs('static/drawings', exist_ok=True)

# ==================== СТРАНИЦЫ ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/draw')
def draw():
    return render_template('draw.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

# ==================== ПРОСТОЙ API ====================

# Хранилище в памяти (вместо базы данных)
drawings_storage = []
next_id = 1

@app.route('/api/save-drawing', methods=['POST'])
def save_drawing():
    global next_id
    
    try:
        data = request.json
        
        # Создаем простую запись
        drawing = {
            'id': next_id,
            'title': data.get('title', 'Без названия'),
            'description': data.get('description', ''),
            'user_name': 'Тестовый художник',
            'likes': 0,
            'url': 'https://via.placeholder.com/400x300/667eea/ffffff?text=Рисунок',
            'date': '2024-01-22'
        }
        
        drawings_storage.append(drawing)
        next_id += 1
        
        return jsonify({'success': True, 'drawing': drawing})
    except:
        return jsonify({'success': False, 'error': 'Ошибка сохранения'})

@app.route('/api/get-drawings')
def get_drawings():
    # Возвращаем тестовые данные
    return jsonify({
        'drawings': [
            {
                'id': 1,
                'title': 'Пример работы 1',
                'user_name': 'Художник 1',
                'likes': 5,
                'url': 'https://via.placeholder.com/400x300/667eea/ffffff?text=Пример+1'
            },
            {
                'id': 2,
                'title': 'Пример работы 2',
                'user_name': 'Художник 2',
                'likes': 12,
                'url': 'https://via.placeholder.com/400x300/764ba2/ffffff?text=Пример+2'
            },
            {
                'id': 3,
                'title': 'Пример работы 3',
                'user_name': 'Художник 3',
                'likes': 8,
                'url': 'https://via.placeholder.com/400x300/ff6b81/ffffff?text=Пример+3'
            }
        ]
    })

@app.route('/api/get-shop-items')
def get_shop_items():
    return jsonify({
        'items': [
            {'id': 1, 'name': 'Кисть "Акварель"', 'price': 100, 'type': 'brush'},
            {'id': 2, 'name': 'Кисть "Масло"', 'price': 150, 'type': 'brush'},
            {'id': 3, 'name': 'Золотая рамка', 'price': 200, 'type': 'frame'},
        ]
    })

@app.route('/api/get-user/<user_id>')
def get_user(user_id):
    return jsonify({
        'id': user_id,
        'name': 'Тестовый пользователь',
        'level': 1,
        'balance': 1000,
        'experience': 50
    })

@app.route('/api/like-drawing/<int:drawing_id>', methods=['POST'])
def like_drawing(drawing_id):
    return jsonify({'success': True, 'likes': 15})

# ==================== ЗАПУСК ====================

if __name__ == '__main__':
    print("🚀 Запускаем Drawfy...")
    print("📌 Открой в браузере: http://localhost:5000")
    print("📌 Главная страница: http://localhost:5000/")
    print("📌 Рисование: http://localhost:5000/draw")
    print("📌 Галерея: http://localhost:5000/gallery")
    print("📌 Магазин: http://localhost:5000/shop")
    print("📌 Профиль: http://localhost:5000/profile")
    print("\n✨ Проект запущен! Нажми Ctrl+C чтобы остановить")
    
    app.run(host='0.0.0.0', port=5000, debug=True)