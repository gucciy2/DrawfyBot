@echo off
echo.
echo 🚀 Запускаем Drawfy локальный сервер...
echo.
echo 📍 Открой в браузере: http://localhost:8000
echo.
echo 📍 Страницы проекта:
echo   - Главная:       http://localhost:8000/
echo   - Рисование:     http://localhost:8000/draw
echo   - Галерея:       http://localhost:8000/gallery  
echo   - Магазин:       http://localhost:8000/shop
echo   - Профиль:       http://localhost:8000/profile
echo.
echo ⚠️  Чтобы остановить сервер, нажми Ctrl+C в этом окне
echo.

python -m http.server 8000
pause