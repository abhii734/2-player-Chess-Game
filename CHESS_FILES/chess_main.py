"""handle the main logic of the chess game.responsible for the game loop,user input,and gamestate
"""
import pygame as P
import sys
import os
from chess_engine import GameState, Move
 
board_width = board_height = 512
panel_width = 320  # Increased width for better text visibility
width = board_width + panel_width  # Total window width
height = board_height
dimensions = 8 #8x8 board
SQ_SIZE = board_height // dimensions
MAX_FPS = 240 #extremely high FPS for maximum smoothness
IMAGES = {}
SOUNDS = {}  # Dictionary to store sound effects

# Color themes for the chess board
COLOR_THEMES = {
    "Classic": [P.Color("white"), P.Color("gray")],
    "Wood": [P.Color(240, 217, 181), P.Color(181, 136, 99)],
    "Green": [P.Color(240, 240, 210), P.Color(118, 150, 86)],
    "Blue": [P.Color(222, 227, 230), P.Color(140, 162, 173)],
    "Purple": [P.Color(240, 230, 240), P.Color(150, 120, 180)],
    "Red": [P.Color(255, 240, 240), P.Color(200, 120, 120)],
    "Ocean": [P.Color(230, 245, 255), P.Color(100, 150, 200)]
}

# Current theme
current_theme = "Classic"
board_colors = COLOR_THEMES[current_theme]
  
"""
Initializing a global dictionary of images.This will be called exactly once in the main.
"""
def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = P.transform.scale(P.image.load("images_chess/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #note: we can access an image by saying IMAGES["wp"]

def loadSounds():
    """Load sound effects for the game"""
    try:
        # Initialize pygame mixer for sound
        P.mixer.init()

        # Try to load the piece movement sound
        if os.path.exists("pieces sound.mp3"):
            SOUNDS["move"] = P.mixer.Sound("pieces sound.mp3")
            print("Piece sound loaded successfully!")
        else:
            print("Warning: pieces sound.mp3 not found. Game will run without move sound.")
            SOUNDS["move"] = None

        # Try to load the capture sound
        if os.path.exists("capture.mp3"):
            SOUNDS["capture"] = P.mixer.Sound("capture.mp3")
            print("Capture sound loaded successfully!")
        else:
            print("Warning: capture.mp3 not found. Game will run without capture sound.")
            SOUNDS["capture"] = None

    except Exception as e:
        print(f"Error loading sounds: {e}")
        SOUNDS["move"] = None
        SOUNDS["capture"] = None



def easeInOutQuad(t):
    """Smooth easing function for animation"""
    if t < 0.5:
        return 2 * t * t
    else:
        return -1 + (4 - 2 * t) * t

def easeInOutCubic(t):
    """Ultra-smooth cubic easing function for silky animation"""
    if t < 0.5:
        return 4 * t * t * t
    else:
        p = 2 * t - 2
        return 1 + p * p * p / 2

def easeInOutQuart(t):
    """Even smoother quartic easing for maximum smoothness"""
    if t < 0.5:
        return 8 * t * t * t * t
    else:
        p = t - 1
        return 1 - 8 * p * p * p * p

def easeInOutSine(t):
    """Silky smooth sine-based easing - the smoothest possible"""
    import math
    return -(math.cos(math.pi * t) - 1) / 2

def easeInOutExpo(t):
    """Exponential easing for ultra-fluid motion"""
    import math
    if t == 0:
        return 0
    elif t == 1:
        return 1
    elif t < 0.5:
        return math.pow(2, 20 * t - 10) / 2
    else:
        return (2 - math.pow(2, -20 * t + 10)) / 2

def calculateDirectPath(startRow, startCol, endRow, endCol):
    """Calculate direct path for smooth gliding movement through any squares"""
    # Always use direct path - just start and end points
    path = []
    path.append((startRow, startCol))
    path.append((endRow, endCol))
    return path

"""main driver for the code
"""
def main():
    P.init()
    screen = P.display.set_mode((width, height))
    clock = P.time.Clock()
    screen.fill(P.Color("white"))
    gs = GameState()

    validMoves = gs.getValidMoves()

    loadImages()#only once before the while loop
    loadSounds()#load sound effects
    running = True
    sqSelected = () #no square selected initially
    playerClicks = [] #keeps track of player clicks (two tuples: [(6,4), (4,4)])
    validMovesForSelectedPiece = [] #valid moves for the currently selected piece

    # Animation variables
    animating = False
    animationMove = None
    animationProgress = 0.0
    animationSpeed = 2.5  # Faster but still ultra-smooth
    # Simplified animation variables for direct movement

    # Color panel variables
    selectedThemeIndex = 0
    theme_names = list(COLOR_THEMES.keys())
    showControlsPopup = False
    while running:
        for e in P.event.get():
            if e.type == P.QUIT:
                running = False
            #mouse handler
            elif e.type == P.MOUSEBUTTONDOWN and not animating:  # Prevent input during animation
                location = P.mouse.get_pos()#(x,y) location of mouse

                # Check if click is in panel area
                if location[0] >= board_width:  # Click is in panel area
                    # Controls button area
                    controls_button_rect = P.Rect(board_width + 25, height - 50, 100, 30)
                    if controls_button_rect.collidepoint(location):
                        showControlsPopup = not showControlsPopup
                    elif showControlsPopup:
                        # Check if click is outside popup to close it
                        popup_rect = P.Rect(board_width + 30, height - 220, 260, 180)
                        if not popup_rect.collidepoint(location):
                            showControlsPopup = False
                    continue  # Don't process panel clicks as chess moves

                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col): #clicked same square twice
                    sqSelected = () #deselect
                    playerClicks = [] #clear player clicks
                    validMovesForSelectedPiece = [] #clear valid moves
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) #append for both clicks
                    # Get valid moves for the selected piece
                    validMovesForSelectedPiece = []
                    if len(playerClicks) == 1:  # First click - show valid moves
                        piece = gs.board[row][col]
                        if piece != "--":  # If there's a piece on the selected square
                            allValidMoves = gs.getValidMoves()
                            for move in allValidMoves:
                                if move.startRow == row and move.startCol == col:
                                    validMovesForSelectedPiece.append(move)
                if len(playerClicks) == 2: #after 2 clicks
                    move = Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    print(f"Start: {playerClicks[0]}, End: {playerClicks[1]}")
                    print(f"Piece: {gs.board[playerClicks[0][0]][playerClicks[0][1]]}")
                    validMoves = gs.getValidMoves()
                    print(f"Number of valid moves: {len(validMoves)}")
                    is_valid_fn = getattr(gs, "isValidMove", None)
                    if callable(is_valid_fn):
                        if is_valid_fn(move):
                            # Start animation instead of making move immediately
                            animating = True
                            animationMove = move
                            animationProgress = 0.0
                            # Direct animation - no path needed
                            print("Valid move!")
                        else:
                            print("Invalid move!")
                    else:
                        # Start animation instead of making move immediately
                        animating = True
                        animationMove = move
                        animationProgress = 0.0
                        # Direct animation - no path needed
                    sqSelected = ()
                    playerClicks = []
                    validMovesForSelectedPiece = [] #clear valid moves after move is made
                    #key handlers
            elif e.type == P.KEYDOWN and not animating:  # Prevent input during animation
                if e.key == P.K_z: #undo move
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    validMovesForSelectedPiece = []
                elif e.key == P.K_r:
                    gs.resetGame()
                    sqSelected = ()
                    playerClicks = []
                    validMovesForSelectedPiece = []
                elif e.key == P.K_UP:  # Navigate up in color themes
                    selectedThemeIndex = (selectedThemeIndex - 1) % len(theme_names)
                elif e.key == P.K_DOWN:  # Navigate down in color themes
                    selectedThemeIndex = (selectedThemeIndex + 1) % len(theme_names)
                elif e.key == P.K_RETURN:  # Apply selected theme
                    global current_theme, board_colors
                    current_theme = theme_names[selectedThemeIndex]
                    board_colors = COLOR_THEMES[current_theme]
                elif e.key == P.K_ESCAPE:  # Close controls popup
                    showControlsPopup = False
                elif e.key == P.K_h:  # Toggle controls popup with H key
                    showControlsPopup = not showControlsPopup

        # Handle animation with frame-time smoothing
        if animating:
            deltaTime = clock.get_time() / 1000.0  # Convert to seconds
            # Smooth the delta time to prevent jitter
            smoothedDelta = min(deltaTime, 1.0/60.0)  # Cap at 60fps equivalent for stability
            animationProgress += animationSpeed * smoothedDelta

            # Simple direct animation - no path segments needed
            if animationProgress >= 1.0:
                # Animation complete, make the actual move
                animationProgress = 1.0

                # Check if this move captures any piece before making the move
                isCapture = animationMove.pieceCaptured != "--"
                isKingCapture = animationMove.pieceCaptured[1] == "K" if isCapture else False

                gs.makeMove(animationMove)

                # Play appropriate sound based on move type
                if isCapture and SOUNDS["capture"]:
                    # Any piece captured - play capture sound (especially important for king)
                    SOUNDS["capture"].play()
                    if isKingCapture:
                        print("King captured! Game ending sound played.")
                elif SOUNDS["move"]:
                    # Regular move - play move sound
                    SOUNDS["move"].play()

                # Check if game ended after the move
                if gs.gameEnded:
                    print(f"Game Over! {gs.winner} wins!")
                animating = False
                animationMove = None

        drawGameState(screen, gs, sqSelected, validMovesForSelectedPiece, animating, animationMove, animationProgress, True, selectedThemeIndex, theme_names, showControlsPopup)
        clock.tick(MAX_FPS)
        P.display.flip()

def drawGameState(screen, gs, sqSelected, validMoves, animating=False, animationMove=None, animationProgress=0.0, showColorPanel=False, selectedThemeIndex=0, theme_names=[], showControlsPopup=False):
    drawBoard(screen)#draw squares on the board
    drawHighlights(screen, sqSelected, validMoves)#add highlights to squares on the board
    drawPieces(screen, gs.board, animating, animationMove, animationProgress)#draw pieces on the board

    # Draw color panel if active
    if showColorPanel:
        drawColorPanel(screen, selectedThemeIndex, theme_names, showControlsPopup)

    # Draw game end message if game is over
    if gs.gameEnded:
        drawGameEndMessage(screen, gs.winner)
    
def drawHighlights(screen, sqSelected, validMoves):
    """Draw highlights for selected square and valid moves"""
    if sqSelected != ():
        row, col = sqSelected
        # Highlight selected square with yellow
        s = P.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)  # transparency value 0-255
        s.fill(P.Color('yellow'))
        screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))

        # Highlight valid move squares with green
        s.fill(P.Color('green'))
        for move in validMoves:
            screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def drawBoard(screen):
    global board_colors
    for r in range(dimensions):
        for c in range(dimensions):
            color = board_colors[((r+c)%2)]
            P.draw.rect(screen, color, P.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board, animating=False, animationMove=None, animationProgress=0.0):
    for r in range(dimensions):
        for c in range(dimensions):
            piece = board[r][c]
            if piece != "--":
                # Check if this piece is being animated
                if (animating and animationMove and
                    r == animationMove.startRow and c == animationMove.startCol):

                    # Direct interpolation from start to end position
                    startX = float(animationMove.startCol * SQ_SIZE)
                    startY = float(animationMove.startRow * SQ_SIZE)
                    endX = float(animationMove.endCol * SQ_SIZE)
                    endY = float(animationMove.endRow * SQ_SIZE)

                    # Use the smoothest possible sine-based easing for perfect fluidity
                    smoothProgress = easeInOutSine(animationProgress)
                    currentX = startX + (endX - startX) * smoothProgress
                    currentY = startY + (endY - startY) * smoothProgress

                    # Use floating point coordinates with rounding for smoothest pixel placement
                    pixelX = round(currentX)
                    pixelY = round(currentY)
                    screen.blit(IMAGES[piece], P.Rect(pixelX, pixelY, SQ_SIZE, SQ_SIZE))
                else:
                    # Draw piece normally
                    screen.blit(IMAGES[piece], P.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawColorPanel(screen, selectedThemeIndex, theme_names, showControlsPopup=False):
    """Draw the clean color theme selection panel with minimized controls"""
    # Panel positioned right of the chess board
    panel_x = board_width
    panel_y = 0
    panel_w = panel_width
    panel_h = height

    # Clean background with subtle gradient effect
    panel_surface = P.Surface((panel_w, panel_h))
    for y in range(panel_h):
        gray_value = 45 + int(y * 10 / panel_h)  # Subtle gradient
        color = P.Color(gray_value, gray_value, gray_value + 5)
        P.draw.line(panel_surface, color, (0, y), (panel_w, y))
    screen.blit(panel_surface, (panel_x, panel_y))

    # Vertical separator line
    P.draw.line(screen, P.Color(80, 80, 80), (panel_x, 0), (panel_x, height), 2)

    # Initialize fonts with better sizes for wider panel
    P.font.init()
    title_font = P.font.Font(None, 32)
    theme_font = P.font.Font(None, 24)
    control_font = P.font.Font(None, 20)

    # Title section
    title_y = 30
    title_text = title_font.render("Board Themes", True, P.Color(220, 220, 220))
    title_rect = title_text.get_rect(center=(panel_x + panel_w//2, title_y))
    screen.blit(title_text, title_rect)

    # Underline for title
    underline_y = title_y + 15
    P.draw.line(screen, P.Color(100, 100, 100),
                (panel_x + 20, underline_y), (panel_x + panel_w - 20, underline_y), 1)

    # Theme selection area - compact to fit controls
    themes_start_y = 80
    theme_height = 45  # Reduced height to make room for controls

    for i, theme_name in enumerate(theme_names):
        y_pos = themes_start_y + i * theme_height

        # Theme container with more padding
        theme_rect = P.Rect(panel_x + 20, y_pos, panel_w - 40, theme_height - 5)

        # Selected theme styling
        if i == selectedThemeIndex:
            # Highlight background
            P.draw.rect(screen, P.Color(70, 70, 90), theme_rect, border_radius=8)
            P.draw.rect(screen, P.Color(120, 150, 200), theme_rect, 2, border_radius=8)
            text_color = P.Color(255, 255, 255)
        else:
            # Normal theme styling
            P.draw.rect(screen, P.Color(55, 55, 60), theme_rect, border_radius=6)
            P.draw.rect(screen, P.Color(80, 80, 85), theme_rect, 1, border_radius=6)
            text_color = P.Color(200, 200, 200)

        # Theme name with compact positioning
        theme_text = theme_font.render(theme_name, True, text_color)
        screen.blit(theme_text, (panel_x + 30, y_pos + 8))

        # Color preview - larger, cleaner squares with more space
        colors = COLOR_THEMES[theme_name]
        preview_size = 28  # Larger squares
        preview_spacing = 35  # More spacing
        preview_start_x = panel_x + panel_w - 100  # More space from right edge

        for j, color in enumerate(colors):
            preview_x = preview_start_x + j * preview_spacing
            preview_y = y_pos + 6  # Compact vertical centering

            # Draw color square with shadow effect
            shadow_rect = P.Rect(preview_x + 2, preview_y + 2, preview_size, preview_size)
            P.draw.rect(screen, P.Color(20, 20, 20), shadow_rect, border_radius=5)

            color_rect = P.Rect(preview_x, preview_y, preview_size, preview_size)
            P.draw.rect(screen, color, color_rect, border_radius=5)
            P.draw.rect(screen, P.Color(120, 120, 120), color_rect, 1, border_radius=5)

    # Minimized controls section - just a help button
    help_button_y = height - 50
    help_button_rect = P.Rect(panel_x + 25, help_button_y, 100, 30)

    # Help button styling
    button_color = P.Color(80, 120, 160) if not showControlsPopup else P.Color(100, 140, 180)
    P.draw.rect(screen, button_color, help_button_rect, border_radius=6)
    P.draw.rect(screen, P.Color(120, 160, 200), help_button_rect, 2, border_radius=6)

    # Help button text
    help_text = control_font.render("Help (H)", True, P.Color(255, 255, 255))
    help_text_rect = help_text.get_rect(center=help_button_rect.center)
    screen.blit(help_text, help_text_rect)

    # Current theme indicator - positioned above help button
    current_y = help_button_y - 40
    current_label = control_font.render("Current:", True, P.Color(150, 150, 150))
    current_value = control_font.render(current_theme, True, P.Color(150, 200, 150))
    screen.blit(current_label, (panel_x + 25, current_y))
    screen.blit(current_value, (panel_x + 25, current_y + 18))

    # Draw controls popup if active
    if showControlsPopup:
        drawControlsPopup(screen, panel_x)

def drawControlsPopup(screen, panel_x):
    """Draw the controls help popup"""
    # Popup dimensions and positioning - larger for better readability
    popup_width = 260
    popup_height = 180
    popup_x = panel_x + 30
    popup_y = height - 220

    # Popup background with shadow
    shadow_rect = P.Rect(popup_x + 3, popup_y + 3, popup_width, popup_height)
    P.draw.rect(screen, P.Color(20, 20, 20), shadow_rect, border_radius=8)

    popup_rect = P.Rect(popup_x, popup_y, popup_width, popup_height)
    P.draw.rect(screen, P.Color(50, 50, 55), popup_rect, border_radius=8)
    P.draw.rect(screen, P.Color(120, 160, 200), popup_rect, 2, border_radius=8)

    # Initialize clean fonts for popup
    P.font.init()
    popup_font = P.font.Font(None, 20)  # Larger, cleaner font
    title_font = P.font.Font(None, 24)  # Bigger title
    small_font = P.font.Font(None, 16)  # For footer text

    # Popup title with better styling
    title_text = title_font.render("CONTROLS", True, P.Color(240, 240, 240))
    title_rect = title_text.get_rect(center=(popup_x + popup_width//2, popup_y + 25))
    screen.blit(title_text, title_rect)

    # Underline for title
    underline_y = popup_y + 35
    P.draw.line(screen, P.Color(120, 160, 200),
                (popup_x + 20, underline_y), (popup_x + popup_width - 20, underline_y), 1)

    # Control instructions with cleaner formatting
    controls = [
        ("↑ ↓", "Navigate Themes"),
        ("Enter", "Apply Selected Theme"),
        ("Z", "Undo Last Move"),
        ("R", "Reset Game Board"),
        ("H", "Toggle Help Panel"),
        ("Esc", "Close Help Panel")
    ]

    start_y = popup_y + 50
    for i, (key, action) in enumerate(controls):
        y = start_y + i * 20  # More spacing between lines

        # Draw key in a different color for better readability
        key_text = popup_font.render(key, True, P.Color(150, 200, 255))  # Light blue
        action_text = popup_font.render(f" - {action}", True, P.Color(220, 220, 220))  # White

        screen.blit(key_text, (popup_x + 20, y))
        key_width = key_text.get_width()
        screen.blit(action_text, (popup_x + 20 + key_width, y))

    # Close instruction at bottom with smaller font
    close_text = small_font.render("Click outside or press Esc to close", True, P.Color(160, 160, 160))
    close_rect = close_text.get_rect(center=(popup_x + popup_width//2, popup_y + popup_height - 15))
    screen.blit(close_text, close_rect)

def drawGameEndMessage(screen, winner):
    """Draw game end message overlay"""
    # Create semi-transparent overlay only over the chess board
    overlay = P.Surface((board_width, board_height))
    overlay.set_alpha(180)  # Semi-transparent
    overlay.fill(P.Color('black'))
    screen.blit(overlay, (0, 0))

    # Initialize font
    P.font.init()
    font = P.font.Font(None, 72)
    small_font = P.font.Font(None, 36)

    # Create text surfaces
    game_over_text = font.render("GAME OVER", True, P.Color('white'))
    winner_text = font.render(f"{winner} Wins!", True, P.Color('yellow'))
    restart_text = small_font.render("Press R to restart", True, P.Color('white'))

    # Center the text on the chess board area
    game_over_rect = game_over_text.get_rect(center=(board_width//2, board_height//2 - 60))
    winner_rect = winner_text.get_rect(center=(board_width//2, board_height//2))
    restart_rect = restart_text.get_rect(center=(board_width//2, board_height//2 + 60))

    # Draw the text
    screen.blit(game_over_text, game_over_rect)
    screen.blit(winner_text, winner_rect)
    screen.blit(restart_text, restart_rect)

if __name__ == "__main__":
    main()
    P.quit()
    sys.exit()







