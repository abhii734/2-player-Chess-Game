"""handle the main logic of the chess game.responsible for the game loop,user input,and gamestate
"""
import pygame as P
import sys
import os
from chess_engine import GameState, Move
 
board_width = board_height = 512
left_panel_width = 280  # Left panel for player names
right_panel_width = 320  # Right panel for themes and controls
width = left_panel_width + board_width + right_panel_width  # Total window width
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

    # Try to load images, if not found create text-based pieces
    for piece in pieces:
        try:
            IMAGES[piece] = P.transform.scale(P.image.load("images_chess/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        except FileNotFoundError:
            # Create a text-based piece if image not found
            IMAGES[piece] = createTextPiece(piece)

    print("Images loaded successfully!")

def createTextPiece(piece):
    """Create a text-based piece surface when images are not available"""
    surface = P.Surface((SQ_SIZE, SQ_SIZE))

    # Set background color based on piece color
    if piece[0] == 'w':  # White piece
        surface.fill(P.Color(240, 240, 240))
        text_color = P.Color(0, 0, 0)
    else:  # Black piece
        surface.fill(P.Color(60, 60, 60))
        text_color = P.Color(255, 255, 255)

    # Draw border
    P.draw.rect(surface, P.Color(100, 100, 100), surface.get_rect(), 2)

    # Get piece symbol
    piece_symbols = {
        'p': '♟', 'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚'
    }

    # Initialize font
    P.font.init()
    font = P.font.Font(None, int(SQ_SIZE * 0.7))

    # Create text
    symbol = piece_symbols.get(piece[1], piece[1])
    text = font.render(symbol, True, text_color)

    # Center the text
    text_rect = text.get_rect(center=(SQ_SIZE//2, SQ_SIZE//2))
    surface.blit(text, text_rect)

    return surface

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

    # Player name variables
    whitePlayerName = ""
    blackPlayerName = ""
    inputActive = None  # None, "white", or "black"
    showNameInput = True
    while running:
        for e in P.event.get():
            if e.type == P.QUIT:
                running = False
            #mouse handler
            elif e.type == P.MOUSEBUTTONDOWN and not animating:  # Prevent input during animation
                location = P.mouse.get_pos()#(x,y) location of mouse

                # Check if click is in left panel (player names) or right panel (themes/controls)
                if location[0] < left_panel_width:  # Click is in left panel (player names)
                    # Player name input areas in left panel
                    white_name_rect = P.Rect(20, 120, left_panel_width - 40, 40)
                    black_name_rect = P.Rect(20, 200, left_panel_width - 40, 40)

                    if white_name_rect.collidepoint(location):
                        inputActive = "white"
                    elif black_name_rect.collidepoint(location):
                        inputActive = "black"
                    else:
                        inputActive = None  # Deactivate input if clicking elsewhere in left panel
                    continue  # Don't process panel clicks as chess moves

                elif location[0] >= left_panel_width + board_width:  # Click is in right panel (themes/controls)
                    # Adjust coordinates for right panel
                    right_panel_x = left_panel_width + board_width
                    # Controls button area
                    controls_button_rect = P.Rect(right_panel_x + 25, height - 50, 100, 30)
                    if controls_button_rect.collidepoint(location):
                        showControlsPopup = not showControlsPopup
                    elif showControlsPopup:
                        # Check if click is outside popup to close it
                        popup_rect = P.Rect(right_panel_x + 30, height - 220, 260, 180)
                        if not popup_rect.collidepoint(location):
                            showControlsPopup = False
                    else:
                        inputActive = None  # Deactivate input if clicking elsewhere
                    continue  # Don't process panel clicks as chess moves

                # Adjust coordinates for the board offset by left panel
                board_x = location[0] - left_panel_width
                col = board_x // SQ_SIZE
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
                    # Create a temporary move to check against valid moves
                    tempMove = Move(playerClicks[0], playerClicks[1], gs.board)
                    print(tempMove.getChessNotation())
                    print(f"Start: {playerClicks[0]}, End: {playerClicks[1]}")
                    print(f"Piece: {gs.board[playerClicks[0][0]][playerClicks[0][1]]}")
                    validMoves = gs.getValidMoves()
                    print(f"Number of valid moves: {len(validMoves)}")
                    print(f"En passant square: {gs.enPassantSquare}")

                    # Check for en passant moves specifically
                    en_passant_moves = [m for m in validMoves if m.isEnPassantMove]
                    if en_passant_moves:
                        print(f"En passant moves available: {len(en_passant_moves)}")
                        for ep_move in en_passant_moves:
                            print(f"  {ep_move.getChessNotation()}")

                    # Find the actual valid move that matches the player's input
                    actualMove = None
                    for validMove in validMoves:
                        if (validMove.startRow == tempMove.startRow and
                            validMove.startCol == tempMove.startCol and
                            validMove.endRow == tempMove.endRow and
                            validMove.endCol == tempMove.endCol):
                            actualMove = validMove
                            break

                    if actualMove:
                        # Start animation with the actual valid move (preserves castling flag)
                        animating = True
                        animationMove = actualMove
                        animationProgress = 0.0
                        print("Valid move!")
                        if actualMove.isCastleMove:
                            print("Castling move detected!")
                    else:
                        print("Invalid move!")
                    sqSelected = ()
                    playerClicks = []
                    validMovesForSelectedPiece = [] #clear valid moves after move is made
                    #key handlers
            elif e.type == P.KEYDOWN and not animating:  # Prevent input during animation
                # Handle text input for player names
                if inputActive:
                    if e.key == P.K_RETURN or e.key == P.K_ESCAPE:
                        inputActive = None  # Finish input
                    elif e.key == P.K_BACKSPACE:
                        if inputActive == "white" and len(whitePlayerName) > 0:
                            whitePlayerName = whitePlayerName[:-1]
                        elif inputActive == "black" and len(blackPlayerName) > 0:
                            blackPlayerName = blackPlayerName[:-1]
                    else:
                        # Add character to name (limit to 15 characters)
                        if e.unicode.isprintable() and len(e.unicode) == 1:
                            if inputActive == "white" and len(whitePlayerName) < 15:
                                whitePlayerName += e.unicode
                            elif inputActive == "black" and len(blackPlayerName) < 15:
                                blackPlayerName += e.unicode
                else:
                    # Regular game controls when not typing names
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
                        inputActive = None  # Also deactivate name input
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
                isCapture = animationMove.pieceCaptured != "--" or animationMove.isEnPassantMove
                isKingCapture = animationMove.pieceCaptured[1] == "K" if animationMove.pieceCaptured != "--" else False

                gs.makeMove(animationMove)

                # Check for checkmate/stalemate after the move
                gs.getValidMoves()  # This will trigger checkmate detection

                # Play appropriate sound based on move type
                if isCapture and SOUNDS["capture"]:
                    # Any piece captured (including en passant) - play capture sound
                    SOUNDS["capture"].play()
                    if isKingCapture:
                        print("King captured! Game ending sound played.")
                    elif animationMove.isEnPassantMove:
                        print("En passant capture!")
                elif SOUNDS["move"]:
                    # Regular move - play move sound
                    SOUNDS["move"].play()

                # Check if game ended after the move
                if gs.gameEnded:
                    if gs.winner == "Stalemate":
                        print("Game Over! Stalemate - Draw!")
                    else:
                        # Display winner with player name
                        if gs.winner == "White":
                            winning_player = whitePlayerName if whitePlayerName.strip() else "White Player"
                        elif gs.winner == "Black":
                            winning_player = blackPlayerName if blackPlayerName.strip() else "Black Player"
                        else:
                            winning_player = gs.winner
                        print(f"Game Over! Checkmate - {winning_player} wins!")
                animating = False
                animationMove = None

        drawGameState(screen, gs, sqSelected, validMovesForSelectedPiece, animating, animationMove, animationProgress, True, selectedThemeIndex, theme_names, showControlsPopup, whitePlayerName, blackPlayerName, inputActive)
        clock.tick(MAX_FPS)
        P.display.flip()

def drawGameState(screen, gs, sqSelected, validMoves, animating=False, animationMove=None, animationProgress=0.0, showColorPanel=False, selectedThemeIndex=0, theme_names=[], showControlsPopup=False, whitePlayerName="", blackPlayerName="", inputActive=None):
    # Draw left panel (player names)
    drawLeftPanel(screen, whitePlayerName, blackPlayerName, inputActive, gs.whiteToMove)

    # Draw chess board (offset by left panel)
    drawBoard(screen)
    drawHighlights(screen, sqSelected, validMoves)
    drawPieces(screen, gs.board, animating, animationMove, animationProgress)

    # Draw right panel (themes and controls)
    if showColorPanel:
        drawRightPanel(screen, selectedThemeIndex, theme_names, showControlsPopup)

    # Draw game end message if game is over
    if gs.gameEnded:
        drawGameEndMessage(screen, gs.winner, whitePlayerName, blackPlayerName)
    
def drawHighlights(screen, sqSelected, validMoves):
    """Draw highlights for selected square and valid moves"""
    if sqSelected != ():
        row, col = sqSelected
        # Highlight selected square with yellow
        s = P.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)  # transparency value 0-255
        s.fill(P.Color('yellow'))
        # Offset by left panel width
        screen.blit(s, (left_panel_width + col*SQ_SIZE, row*SQ_SIZE))

        # Highlight valid move squares with green
        s.fill(P.Color('green'))
        for move in validMoves:
            # Offset by left panel width
            screen.blit(s, (left_panel_width + move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def drawBoard(screen):
    global board_colors
    for r in range(dimensions):
        for c in range(dimensions):
            color = board_colors[((r+c)%2)]
            # Offset board by left panel width
            P.draw.rect(screen, color, P.Rect(left_panel_width + c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board, animating=False, animationMove=None, animationProgress=0.0):
    for r in range(dimensions):
        for c in range(dimensions):
            piece = board[r][c]
            if piece != "--":
                # Check if this piece is being animated (king in castling or any other move)
                if (animating and animationMove and
                    r == animationMove.startRow and c == animationMove.startCol):

                    # Direct interpolation from start to end position (offset by left panel)
                    startX = float(left_panel_width + animationMove.startCol * SQ_SIZE)
                    startY = float(animationMove.startRow * SQ_SIZE)
                    endX = float(left_panel_width + animationMove.endCol * SQ_SIZE)
                    endY = float(animationMove.endRow * SQ_SIZE)

                    # Use the smoothest possible sine-based easing for perfect fluidity
                    smoothProgress = easeInOutSine(animationProgress)
                    currentX = startX + (endX - startX) * smoothProgress
                    currentY = startY + (endY - startY) * smoothProgress

                    # Use floating point coordinates with rounding for smoothest pixel placement
                    pixelX = round(currentX)
                    pixelY = round(currentY)
                    screen.blit(IMAGES[piece], P.Rect(pixelX, pixelY, SQ_SIZE, SQ_SIZE))

                # Check if this is a pawn being captured by en passant (should be hidden during animation)
                elif (animating and animationMove and animationMove.isEnPassantMove and
                      r == animationMove.startRow and c == animationMove.endCol):
                    # Don't draw the captured pawn during en passant animation
                    continue

                # Check if this is a rook being animated during castling
                elif (animating and animationMove and animationMove.isCastleMove and
                      piece[1] == "R" and piece[0] == animationMove.pieceMoved[0]):  # Same color rook

                    # Determine rook movement based on castling direction
                    if animationMove.endCol - animationMove.startCol == 2:  # King-side castle
                        if c == 7 and r == animationMove.startRow:  # King-side rook position
                            # Animate rook from h-file to f-file (offset by left panel)
                            startX = float(left_panel_width + 7 * SQ_SIZE)
                            startY = float(r * SQ_SIZE)
                            endX = float(left_panel_width + 5 * SQ_SIZE)
                            endY = float(r * SQ_SIZE)

                            smoothProgress = easeInOutSine(animationProgress)
                            currentX = startX + (endX - startX) * smoothProgress
                            currentY = startY + (endY - startY) * smoothProgress

                            pixelX = round(currentX)
                            pixelY = round(currentY)
                            screen.blit(IMAGES[piece], P.Rect(pixelX, pixelY, SQ_SIZE, SQ_SIZE))
                        else:
                            # Draw rook normally if it's not the castling rook (offset by left panel)
                            screen.blit(IMAGES[piece], P.Rect(left_panel_width + c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

                    elif animationMove.endCol - animationMove.startCol == -2:  # Queen-side castle
                        if c == 0 and r == animationMove.startRow:  # Queen-side rook position
                            # Animate rook from a-file to d-file (offset by left panel)
                            startX = float(left_panel_width + 0 * SQ_SIZE)
                            startY = float(r * SQ_SIZE)
                            endX = float(left_panel_width + 3 * SQ_SIZE)
                            endY = float(r * SQ_SIZE)

                            smoothProgress = easeInOutSine(animationProgress)
                            currentX = startX + (endX - startX) * smoothProgress
                            currentY = startY + (endY - startY) * smoothProgress

                            pixelX = round(currentX)
                            pixelY = round(currentY)
                            screen.blit(IMAGES[piece], P.Rect(pixelX, pixelY, SQ_SIZE, SQ_SIZE))
                        else:
                            # Draw rook normally if it's not the castling rook (offset by left panel)
                            screen.blit(IMAGES[piece], P.Rect(left_panel_width + c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                    else:
                        # Draw rook normally for non-castling moves (offset by left panel)
                        screen.blit(IMAGES[piece], P.Rect(left_panel_width + c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                else:
                    # Draw piece normally (offset by left panel)
                    screen.blit(IMAGES[piece], P.Rect(left_panel_width + c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawLeftPanel(screen, whitePlayerName="", blackPlayerName="", inputActive=None, whiteToMove=True):
    """Draw the cool left panel with player names and game info"""
    import math
    import time

    # Panel dimensions
    panel_w = left_panel_width
    panel_h = height

    # Create gradient background
    panel_surface = P.Surface((panel_w, panel_h))
    for y in range(panel_h):
        # Cool gradient from dark blue to darker blue
        blue_value = 25 + int(y * 15 / panel_h)
        color = P.Color(blue_value//3, blue_value//2, blue_value)
        P.draw.line(panel_surface, color, (0, y), (panel_w, y))
    screen.blit(panel_surface, (0, 0))

    # Add some animated elements
    current_time = time.time()

    # Initialize fonts
    P.font.init()
    title_font = P.font.Font(None, 36)
    player_font = P.font.Font(None, 28)
    input_font = P.font.Font(None, 24)
    small_font = P.font.Font(None, 20)

    # Title with glow effect
    title_y = 30
    title_text = "CHESS PLAYERS"

    # Draw title with glow effect
    for offset in range(3, 0, -1):
        glow_color = P.Color(50, 100, 200, 100 - offset * 30)
        glow_surface = title_font.render(title_text, True, glow_color)
        glow_rect = glow_surface.get_rect(center=(panel_w//2 + offset, title_y + offset))
        screen.blit(glow_surface, glow_rect)

    # Main title
    title_surface = title_font.render(title_text, True, P.Color(255, 255, 255))
    title_rect = title_surface.get_rect(center=(panel_w//2, title_y))
    screen.blit(title_surface, title_rect)

    # Animated underline
    underline_y = title_y + 25
    wave_offset = math.sin(current_time * 3) * 5
    for i in range(panel_w - 40):
        x = 20 + i
        wave_y = underline_y + math.sin((i + current_time * 50) * 0.1) * 2
        color_intensity = 150 + int(math.sin((i + current_time * 30) * 0.05) * 50)
        P.draw.circle(screen, P.Color(color_intensity, color_intensity//2, 255), (int(x), int(wave_y)), 1)

    # White Player Section
    white_y = 90
    white_label = player_font.render("WHITE PLAYER", True, P.Color(255, 255, 255))
    screen.blit(white_label, (20, white_y))

    # White player input box with cool styling
    white_input_rect = P.Rect(20, white_y + 30, panel_w - 40, 40)

    # Animated border for active input
    if inputActive == "white":
        # Pulsing border animation
        pulse = math.sin(current_time * 8) * 0.3 + 0.7
        border_color = P.Color(int(100 * pulse), int(200 * pulse), int(255 * pulse))
        for i in range(3):
            border_rect = P.Rect(white_input_rect.x - i, white_input_rect.y - i,
                               white_input_rect.width + 2*i, white_input_rect.height + 2*i)
            P.draw.rect(screen, border_color, border_rect, 1, border_radius=8)

    # Input box background
    input_bg_color = P.Color(40, 60, 100) if inputActive == "white" else P.Color(30, 45, 75)
    P.draw.rect(screen, input_bg_color, white_input_rect, border_radius=8)
    P.draw.rect(screen, P.Color(100, 150, 255), white_input_rect, 2, border_radius=8)

    # Display white player name
    display_name = whitePlayerName if whitePlayerName else "Click to enter name..."
    name_color = P.Color(255, 255, 255) if whitePlayerName else P.Color(150, 150, 150)
    white_name_surface = input_font.render(display_name, True, name_color)
    screen.blit(white_name_surface, (white_input_rect.x + 15, white_input_rect.y + 10))



    # Current turn indicator for white with animation
    if whiteToMove:
        turn_text = "◄ YOUR TURN"
        turn_color = P.Color(100, 255, 100)
        # Pulsing effect
        pulse = math.sin(current_time * 4) * 0.2 + 0.8
        turn_color = P.Color(int(100 * pulse), int(255 * pulse), int(100 * pulse))
        turn_surface = small_font.render(turn_text, True, turn_color)
        screen.blit(turn_surface, (25, white_y + 75))

    # Black Player Section
    black_y = 180
    black_label = player_font.render("BLACK PLAYER", True, P.Color(200, 200, 200))
    screen.blit(black_label, (20, black_y))

    # Black player input box
    black_input_rect = P.Rect(20, black_y + 30, panel_w - 40, 40)

    # Animated border for active input
    if inputActive == "black":
        # Pulsing border animation
        pulse = math.sin(current_time * 8) * 0.3 + 0.7
        border_color = P.Color(int(255 * pulse), int(200 * pulse), int(100 * pulse))
        for i in range(3):
            border_rect = P.Rect(black_input_rect.x - i, black_input_rect.y - i,
                               black_input_rect.width + 2*i, black_input_rect.height + 2*i)
            P.draw.rect(screen, border_color, border_rect, 1, border_radius=8)

    # Input box background
    input_bg_color = P.Color(60, 40, 20) if inputActive == "black" else P.Color(45, 30, 15)
    P.draw.rect(screen, input_bg_color, black_input_rect, border_radius=8)
    P.draw.rect(screen, P.Color(200, 150, 100), black_input_rect, 2, border_radius=8)

    # Display black player name
    display_name = blackPlayerName if blackPlayerName else "Click to enter name..."
    name_color = P.Color(255, 255, 255) if blackPlayerName else P.Color(150, 150, 150)
    black_name_surface = input_font.render(display_name, True, name_color)
    screen.blit(black_name_surface, (black_input_rect.x + 15, black_input_rect.y + 10))



    # Current turn indicator for black with animation
    if not whiteToMove:
        turn_text = "◄ YOUR TURN"
        # Pulsing effect
        pulse = math.sin(current_time * 4) * 0.2 + 0.8
        turn_color = P.Color(int(255 * pulse), int(200 * pulse), int(100 * pulse))
        turn_surface = small_font.render(turn_text, True, turn_color)
        screen.blit(turn_surface, (25, black_y + 75))

    # Game info section
    info_y = 300
    info_title = player_font.render("GAME INFO", True, P.Color(200, 200, 255))
    screen.blit(info_title, (20, info_y))

    # Add some game statistics or tips
    tips = [
        "• Click piece to select",
        "• Green squares = valid moves",
        "• Yellow = selected piece",
        "• Z = Undo move",
        "• R = Reset game",
        "• H = Help"
    ]

    for i, tip in enumerate(tips):
        tip_surface = small_font.render(tip, True, P.Color(180, 180, 200))
        screen.blit(tip_surface, (25, info_y + 30 + i * 20))

    # Vertical separator line with glow
    separator_x = panel_w - 1
    for i in range(3):
        line_color = P.Color(100 - i * 30, 150 - i * 40, 255 - i * 50)
        P.draw.line(screen, line_color, (separator_x - i, 0), (separator_x - i, height), 1)

def drawRightPanel(screen, selectedThemeIndex, theme_names, showControlsPopup=False):
    """Draw the clean color theme selection panel with minimized controls"""
    # Panel positioned right of the chess board
    panel_x = left_panel_width + board_width
    panel_y = 0
    panel_w = right_panel_width
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

    # Board Themes Section
    themes_title_y = 30
    themes_title = title_font.render("Board Themes", True, P.Color(220, 220, 220))
    themes_title_rect = themes_title.get_rect(center=(panel_x + panel_w//2, themes_title_y))
    screen.blit(themes_title, themes_title_rect)

    # Underline for themes section
    themes_underline_y = themes_title_y + 15
    P.draw.line(screen, P.Color(100, 100, 100),
                (panel_x + 20, themes_underline_y), (panel_x + panel_w - 20, themes_underline_y), 1)

    # Theme selection area - more space now that player names are on left
    themes_start_y = 70
    theme_height = 45  # More height since we have more space

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



def drawGameEndMessage(screen, winner, whitePlayerName="", blackPlayerName=""):
    """Draw game end message overlay with player names"""
    # Create semi-transparent overlay only over the chess board
    overlay = P.Surface((board_width, board_height))
    overlay.set_alpha(180)  # Semi-transparent
    overlay.fill(P.Color('black'))
    # Position overlay over the chess board (offset by left panel)
    screen.blit(overlay, (left_panel_width, 0))

    # Initialize font
    P.font.init()
    font = P.font.Font(None, 72)
    small_font = P.font.Font(None, 36)

    # Create text surfaces based on game result
    if winner == "Stalemate":
        game_over_text = font.render("STALEMATE", True, P.Color('orange'))
        winner_text = font.render("Game is a Draw!", True, P.Color('yellow'))
    else:
        game_over_text = font.render("CHECKMATE", True, P.Color('red'))

        # Determine the winning player's name and create winner text
        if winner == "White":
            player_name = whitePlayerName if whitePlayerName.strip() else "White Player"
            if whitePlayerName.strip():
                winner_text = font.render(f"{player_name} Wins!", True, P.Color('yellow'))
                color_text = small_font.render("(Playing as White)", True, P.Color('lightgray'))
            else:
                winner_text = font.render("White Wins!", True, P.Color('yellow'))
                color_text = None
        elif winner == "Black":
            player_name = blackPlayerName if blackPlayerName.strip() else "Black Player"
            if blackPlayerName.strip():
                winner_text = font.render(f"{player_name} Wins!", True, P.Color('yellow'))
                color_text = small_font.render("(Playing as Black)", True, P.Color('lightgray'))
            else:
                winner_text = font.render("Black Wins!", True, P.Color('yellow'))
                color_text = None
        else:
            winner_text = font.render(f"{winner} Wins!", True, P.Color('yellow'))
            color_text = None

    restart_text = small_font.render("Press R to restart", True, P.Color('white'))

    # Center the text on the chess board area (accounting for left panel offset)
    board_center_x = left_panel_width + board_width//2
    board_center_y = board_height//2

    # Adjust positioning based on whether we have color text
    if winner != "Stalemate" and color_text:
        game_over_rect = game_over_text.get_rect(center=(board_center_x, board_center_y - 80))
        winner_rect = winner_text.get_rect(center=(board_center_x, board_center_y - 20))
        color_rect = color_text.get_rect(center=(board_center_x, board_center_y + 10))
        restart_rect = restart_text.get_rect(center=(board_center_x, board_center_y + 60))
    else:
        game_over_rect = game_over_text.get_rect(center=(board_center_x, board_center_y - 60))
        winner_rect = winner_text.get_rect(center=(board_center_x, board_center_y))
        restart_rect = restart_text.get_rect(center=(board_center_x, board_center_y + 60))

    # Draw the text
    screen.blit(game_over_text, game_over_rect)
    screen.blit(winner_text, winner_rect)

    # Draw color text if it exists
    if winner != "Stalemate" and color_text:
        screen.blit(color_text, color_rect)

    screen.blit(restart_text, restart_rect)

if __name__ == "__main__":
    main()
    P.quit()
    sys.exit()







