import os

def fix_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем ссылки
    replacements = {
        'href="/draw"': 'href="draw.html"',
        'href="/gallery"': 'href="gallery.html"',
        'href="/shop"': 'href="shop.html"',
        'href="/profile"': 'href="profile.html"',
        'href="/"': 'href="index.html"',
        'href="/static/css/style.css"': 'href="../static/css/style.css"',
        'src="/static/css/style.css"': 'src="../static/css/style.css"',
        '"/api/': '"http://localhost:5000/api/',
        'window.location.href = \'/gallery\'': 'window.location.href = \'gallery.html\'',
        'window.location.href = \'/draw\'': 'window.location.href = \'draw.html\'',
        'window.location.href = \'/shop\'': 'window.location.href = \'shop.html\'',
        'window.location.href = \'/profile\'': 'window.location.href = \'profile.html\'',
        'window.location.href = \'/\'': 'window.location.href = \'index.html\'',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Исправлен: {filepath}")

# Исправляем все HTML файлы
templates_dir = "templates"
for filename in os.listdir(templates_dir):
    if filename.endswith(".html"):
        fix_html_file(os.path.join(templates_dir, filename))

print("🎉 Все файлы исправлены!")
print("📂 Теперь открой templates/index.html в браузере")