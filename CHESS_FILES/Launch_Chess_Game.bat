@echo off
title 🏆 Enhanced Chess Game Launcher 🏆
color 0B
cls
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                              ║
echo  ║        🏆 ENHANCED CHESS GAME LAUNCHER 🏆                   ║
echo  ║                                                              ║
echo  ║    ♔ ♕ ♖ ♗ ♘ ♙    Welcome to Chess!    ♟ ♞ ♝ ♜ ♛ ♚    ║
echo  ║                                                              ║
echo  ║         • Ultra-smooth animations                            ║
echo  ║         • 7 beautiful color themes                           ║
echo  ║         • Sound effects ^& music                              ║
echo  ║         • Professional UI design                             ║
echo  ║                                                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  🔍 Performing system checks...
echo.

REM Check if Python is installed
echo  [1/4] 🐍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ ERROR: Python is not installed or not in PATH
    echo  💡 Please install Python from https://python.org
    echo.
    pause
    exit /b 1
) else (
    echo  ✅ Python is installed and ready!
)

REM Check if required files exist
echo  [2/4] 📁 Checking game files...
if not exist "chess_main.py" (
    echo  ❌ ERROR: chess_main.py not found!
    echo  💡 Please ensure all game files are in the same directory.
    echo.
    pause
    exit /b 1
) else (
    echo  ✅ chess_main.py found
)

if not exist "chess_engine.py" (
    echo  ❌ ERROR: chess_engine.py not found!
    echo  💡 Please ensure all game files are in the same directory.
    echo.
    pause
    exit /b 1
) else (
    echo  ✅ chess_engine.py found
)

REM Check if images folder exists
echo  [3/4] 🎨 Checking chess piece images...
if not exist "images_chess" (
    echo  ❌ ERROR: images_chess folder not found!
    echo  💡 Please ensure the chess piece images are in the images_chess folder.
    echo.
    pause
    exit /b 1
) else (
    echo  ✅ Chess piece images found
)

REM Install required packages if needed
echo  [4/4] 🎮 Checking game dependencies...
echo  📦 Installing/updating pygame (this may take a moment)...
pip install pygame >nul 2>&1
if errorlevel 1 (
    echo  ⚠️  Warning: Could not install pygame automatically
    echo  💡 You may need to install it manually: pip install pygame
) else (
    echo  ✅ Pygame is ready!
)

echo.
echo  🎉 All checks passed! Ready to play!
echo  ✨ Your chess game is fully configured and ready!
echo.
pause

REM Launch the game
cls
echo.
echo  ══════════════════════════════════════════════════════════════
echo     🚀 LAUNCHING ENHANCED CHESS GAME 🚀
echo  ══════════════════════════════════════════════════════════════
echo.
echo     🎯 Get ready for an amazing chess experience!
echo     ♔ Features: Smooth animations, themes, sounds ^& more!
echo.
echo     Starting in 3...
timeout /t 1 >nul
echo     Starting in 2...
timeout /t 1 >nul
echo     Starting in 1...
timeout /t 1 >nul
echo     🎮 Starting game now!
echo.

python chess_main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo  😞 Game exited with an error.
    echo  💡 Please check that all files are present and try again.
    echo.
    pause
) else (
    echo.
    echo  ══════════════════════════════════════════════════════════════
    echo     🏆 Game session ended. Thanks for playing!
    echo     👋 Hope you enjoyed the Enhanced Chess Game!
    echo  ══════════════════════════════════════════════════════════════
    echo.
    pause
)
