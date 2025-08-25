# Enhanced Chess Game 🏆

A beautiful, feature-rich chess game built with Python and Pygame, featuring smooth animations, multiple color themes, sound effects, and an intuitive user interface.

## 🎮 Features

### Game Features
- **Ultra-smooth animations** with sine-based easing for piece movements
- **Move highlights** showing valid moves for selected pieces
- **Game end detection** with winner announcement when king is captured
- **Sound effects** for moves and captures
- **Undo/Redo functionality** with Z key
- **Game reset** with R key

### Visual Enhancements
- **7 Beautiful Color Themes**:
  - Classic (White & Gray)
  - Wood (Warm wooden tones)
  - Green (Tournament style)
  - Blue (Cool blue tones)
  - Purple (Elegant purple)
  - Red (Warm red theme)
  - Ocean (Calming blues)
- **Professional UI panel** with theme selection
- **Clean, modern design** with rounded corners and shadows
- **240 FPS rendering** for maximum smoothness

### Audio
- **Move sounds** (`pieces sound.mp3`) for regular piece movements
- **Capture sounds** (`capture.mp3`) for piece captures
- **Automatic sound detection** - game works with or without sound files

## 🚀 How to Launch the Game

### Option 1: User-Friendly Python Launcher ⭐ (Recommended)
```bash
python launch_game.py
```
**Features:**
- 🎨 Beautiful ASCII art banner
- 📋 Step-by-step system checks with emojis
- 🔄 Automatic pygame installation with progress bars
- 🔊 Sound file detection and status
- ⏱️ Smooth countdown before game launch
- 🛡️ Comprehensive error handling and troubleshooting

### Option 2: Enhanced Windows Batch Launcher
Double-click `Launch_Chess_Game.bat` on Windows systems.
**Features:**
- 🎨 Colorful Windows interface
- ✅ Visual check marks for each step
- 📦 Automatic dependency installation
- ⏰ Countdown timer before launch
- 🎯 Professional error messages

### Option 3: Direct Launch (Advanced Users)
```bash
python chess_main.py
```

## 🎯 How to Play

### Basic Controls
- **Mouse**: Click to select pieces and make moves
- **↑/↓ Arrow Keys**: Navigate through color themes
- **Enter**: Apply selected color theme
- **Z**: Undo last move
- **R**: Reset game
- **H**: Toggle help panel
- **Esc**: Close help panel

### Gameplay
1. Click on a piece to select it (highlights will show valid moves)
2. Click on a highlighted square to move the piece
3. Pieces will glide smoothly to their destination
4. Capture opponent pieces to gain advantage
5. Capture the enemy king to win the game!

## 📁 File Structure

```
Enhanced Chess Game/
├── chess_main.py              # Main game file
├── chess_engine.py            # Game logic and rules
├── launch_game.py             # Python launcher (recommended)
├── Launch_Chess_Game.bat      # Windows batch launcher
├── images_chess/              # Chess piece images
│   ├── wK.png, wQ.png, etc.  # White pieces
│   └── bK.png, bQ.png, etc.  # Black pieces
├── pieces sound.mp3           # Move sound effect
├── capture.mp3               # Capture sound effect
└── README.md                 # This file
```

## 🔧 Requirements

- **Python 3.6+**
- **Pygame** (automatically installed by launcher)
- **Windows/Mac/Linux** compatible

## 🎨 Color Themes

The game includes 7 beautiful color themes accessible through the side panel:

1. **Classic** - Traditional white and gray
2. **Wood** - Warm wooden chess board colors  
3. **Green** - Tournament-style green and cream
4. **Blue** - Cool, calming blue tones
5. **Purple** - Elegant purple theme
6. **Red** - Warm red theme
7. **Ocean** - Soothing ocean blues

Use ↑/↓ arrow keys to browse themes and Enter to apply them instantly!

## 🔊 Sound Effects

- Place `pieces sound.mp3` in the game folder for move sounds
- Place `capture.mp3` in the game folder for capture sounds
- Game works perfectly without sound files (silent mode)

## 🏁 Getting Started

1. **Download/Clone** the game files
2. **Run the launcher**: `python launch_game.py`
3. **Start playing** and enjoy the smooth, beautiful chess experience!

## 🎯 Tips

- **Smooth animations**: Pieces glide beautifully across the board
- **Visual feedback**: Selected pieces and valid moves are highlighted
- **Theme switching**: Change board colors anytime during gameplay
- **Audio cues**: Different sounds for moves vs captures
- **Help system**: Press H for controls reminder

---

**Enjoy your enhanced chess gaming experience!** 🏆♟️
