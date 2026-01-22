import os

# Список всех HTML файлов
html_files = [
    "templates/index.html",
    "templates/draw.html", 
    "templates/gallery.html",
    "templates/shop.html",
    "templates/profile.html"
]

print("🔧 Исправляем пути к CSS файлам...")

for file_path in html_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Исправляем путь к CSS
        old_css = 'href="/static/css/style.css"'
        new_css = 'href="../static/css/style.css"'
        
        if old_css in content:
            content = content.replace(old_css, new_css)
            print(f"✅ Исправлен: {file_path}")
        else:
            # Пробуем другой вариант
            old_css2 = 'href="/static/css/style.css"'
            if old_css2 in content:
                content = content.replace(old_css2, new_css)
                print(f"✅ Исправлен (вариант 2): {file_path}")
        
        # Сохраняем исправленный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        print(f"❌ Ошибка в файле {file_path}: {e}")

print("\n🎉 Все файлы исправлены!")
print("\n📌 Теперь открой любой HTML файл из папки templates/")