@echo off
echo 🗺️ Downloading West Bengal City Maps...

call venv\Scripts\activate.bat

echo 📋 Available West Bengal cities:
python download_real_map.py --west-bengal

echo.
echo 🎯 Downloading Kolkata (capital city)...
python download_real_map.py kolkata

echo.
echo 🎯 Downloading Durgapur (industrial city)...
python download_real_map.py durgapur

echo.
echo 🎯 Downloading Siliguri (northeast gateway)...
python download_real_map.py siliguri

echo.
echo ✅ Map download complete!
echo.
pause