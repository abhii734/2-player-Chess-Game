"""handle the main logic of the chess game.responsible for the game loop,user input,and gamestate
"""
import pygame as P
import sys
import os
from chess_engine import GameState, Move
 
width = height = 512 
dimensions = 8 #8x8 board
SQ_SIZE = height // dimensions
MAX_FPS = 15 #mainly for animation
IMAGES = {}
  
"""
Initializing a global dictionary of images.This will be called exactly once in the main.
"""

def resource_path(relative_path):
    """Return absolute path to resource, works for dev and PyInstaller onefile."""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)
def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        img_path = resource_path("images_chess/" + piece + ".png")
        IMAGES[piece] = P.transform.scale(P.image.load(img_path), (SQ_SIZE, SQ_SIZE))
    #note: we can access an image by saying IMAGES["wp"]

"""main driver for the code
"""
def main():
    P.init()
    screen = P.display.set_mode((width, height))
    clock = P.time.Clock()
    screen.fill(P.Color("white"))
    gs = GameState()
    validMoves = gs.getValidMoves()
    moveMade = False

    loadImages()#only once before the while loop
    running = True
    sqSelected = () #no square selected initially
    playerClicks = [] #keeps track of player clicks (two tuples: [(6,4), (4,4)])
    while running:
        for e in P.event.get():
            if e.type == P.QUIT:
                running = False
            #mouse handler
            elif e.type == P.MOUSEBUTTONDOWN:
                location = P.mouse.get_pos()#(x,y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col): #clicked same square twice
                    sqSelected = () #deselect
                    playerClicks = [] #clear player clicks
                else:
                    if len(playerClicks) == 0:
                        piece_at_square = gs.board[row][col]
                        if piece_at_square != "--" and ((piece_at_square[0] == "w" and gs.whiteToMove) or (piece_at_square[0] == "b" and not gs.whiteToMove)):
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected)
                        else:
                            # ignore selecting empty square or opponent piece as start
                            pass
                    else:
                        # have a start square already; this is the destination
                        playerClicks.append((row, col))
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
                            gs.makeMove(move)
                            moveMade = True
                            print("Valid move!")
                        else:
                            print("Invalid move!")
                    else:
                        gs.makeMove(move)
                        moveMade = True
                    sqSelected = ()
                    playerClicks = []
                    #key handlers
            elif e.type == P.KEYDOWN:
                if e.key == P.K_z: #undo move
                    gs.undoMove()
                    moveMade = True
                    sqSelected = ()
                    playerClicks = []
                if e.key == P.K_r:
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []

                    


        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        P.display.flip()


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)#draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)#draw pieces on the board
    
def drawBoard(screen):
    colors = [P.Color("white"), P.Color("gray")]
    for r in range(dimensions):
        for c in range(dimensions):
            color = colors[((r+c)%2)]
            P.draw.rect(screen, color, P.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        piece = gs.board[r][c]
        if piece != "--" and ((piece[0] == "w" and gs.whiteToMove) or (piece[0] == "b" and not gs.whiteToMove)):
            surface = P.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)
            # highlight selected square
            surface.fill(P.Color("yellow"))
            screen.blit(surface, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight valid destination squares
            surface.fill(P.Color("green"))
            for m in validMoves:
                if m.startRow == r and m.startCol == c:
                    screen.blit(surface, (m.endCol * SQ_SIZE, m.endRow * SQ_SIZE))
def drawPieces(screen, board):
    for r in range(dimensions):
        for c in range(dimensions):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], P.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()
    P.quit()
    sys.exit()







