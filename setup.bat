@echo off
echo 🚀 Setting up Smart Route Assistant for West Bengal...

:: Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

:: Activate environment
echo 🔧 Activating environment...
call venv\Scripts\activate.bat

:: Install requirements
echo 📥 Installing dependencies...
pip install numpy tensorflow matplotlib pandas requests traci sumolib gym

:: Create directories
echo 📁 Creating project structure...
mkdir brain settings map_downloader city_maps memories results 2>nul

:: Create default network
echo 🏗️ Creating default city network...
python create_network.py

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Run the project: run_project.bat
echo 2. Or download cities: download_maps.bat
echo.
pause