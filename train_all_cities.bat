@echo off
call venv\Scripts\activate.bat

echo 🏙️ Training AI on multiple West Bengal cities...

echo 🎯 Training on Kolkata...
python assistant.py --city kolkata --days 30 --no-gui

echo 🎯 Training on Durgapur...
python assistant.py --city durgapur --days 30 --no-gui

echo 🎯 Training on Siliguri...
python assistant.py --city siliguri --days 30 --no-gui

echo ✅ All cities trained!
pause