@echo off
title Smart Route Assistant - West Bengal
echo 🚗 Smart Route Assistant - West Bengal Edition
echo ==============================================

call venv\Scripts\activate.bat

echo 🏙️ Available cities in your system:
dir city_maps\real_cities\*.net.xml /b 2>nul

echo.
echo 🧠 Starting AI Training...
echo 💡 This will train the AI to optimize routes in Kolkata
echo ⏰ This may take several minutes...
echo.

python assistant.py --city kolkata --days 50 --no-gui

echo.
echo ✅ Training completed!
echo 📊 Check 'results' folder for progress charts
echo 💾 Check 'memories' folder for trained models
echo.
pause