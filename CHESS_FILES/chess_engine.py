"""responsible for storing the gamestate , validating moves , and checking for checkmate and vaid moves at the current state
keep move log and history of the game
"""
class GameState():
    def __init__(self):
        #board is an 8x8 2d list , each element has 2 characters
        #first character is the color of the piece "w" or "b"
        #second character is the type of the piece "R" , "N" , "B" , "Q" , "K" , "P"
        #"--" represents an empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.whiteToMove = True
        self.moveLog = []
        # Castling rights: [wK, wQ, bK, bQ] - King-side and Queen-side for both colors
        self.castlingRights = [True, True, True, True]
        # Game end tracking
        self.gameEnded = False
        self.winner = None  # "White" or "Black"

    def makeMove(self, move):
        # Handle castling FIRST (before moving the king)
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # King-side castle
                # Move rook first
                rookRow = move.startRow
                rookStartCol = 7
                rookEndCol = 5
                rookPiece = self.board[rookRow][rookStartCol]  # Store rook piece
                self.board[rookRow][rookEndCol] = rookPiece
                self.board[rookRow][rookStartCol] = "--"
            else:  # Queen-side castle
                # Move rook first
                rookRow = move.startRow
                rookStartCol = 0
                rookEndCol = 3
                rookPiece = self.board[rookRow][rookStartCol]  # Store rook piece
                self.board[rookRow][rookEndCol] = rookPiece
                self.board[rookRow][rookStartCol] = "--"
        
        # Check for king capture before making the move
        if move.pieceCaptured[1] == "K":  # King is being captured
            self.gameEnded = True
            # The player making the move wins
            self.winner = "White" if self.whiteToMove else "Black"

        # Now move the king (or any other piece)
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #to undo moves later on
        self.whiteToMove = not self.whiteToMove #swap btw players

        # Update castling rights
        self.updateCastlingRights(move)

    def updateCastlingRights(self, move):
        # If king moves, lose all castling rights for that color
        if move.pieceMoved[1] == "K":
            if move.pieceMoved[0] == "w":
                self.castlingRights[0] = False  # wK
                self.castlingRights[1] = False  # wQ
            else:
                self.castlingRights[2] = False  # bK
                self.castlingRights[3] = False  # bQ
        
        # If rook moves, lose castling rights for that side
        elif move.pieceMoved[1] == "R":
            if move.pieceMoved[0] == "w":
                if move.startCol == 7:  # King-side rook
                    self.castlingRights[0] = False  # wK
                elif move.startCol == 0:  # Queen-side rook
                    self.castlingRights[1] = False  # wQ
            else:
                if move.startCol == 7:  # King-side rook
                    self.castlingRights[2] = False  # bK
                elif move.startCol == 0:  # Queen-side rook
                    self.castlingRights[3] = False  # bQ
        
        # If rook is captured, lose castling rights for that side
        if move.pieceCaptured[1] == "R":
            if move.pieceCaptured[0] == "w":
                if move.endCol == 7:  # King-side rook
                    self.castlingRights[0] = False  # wK
                elif move.endCol == 0:  # Queen-side rook
                    self.castlingRights[1] = False  # wQ
            else:
                if move.endCol == 7:  # King-side rook
                    self.castlingRights[2] = False  # bK
                elif move.endCol == 0:  # Queen-side rook
                    self.castlingRights[3] = False  # bQ
        
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()

            # If undoing a move that ended the game, reset game state
            if move.pieceCaptured[1] == "K":
                self.gameEnded = False
                self.winner = None

            # First restore the king (or any other piece)
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            
            # Handle castling undo (after restoring the king)
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # King-side castle
                    # Move rook back
                    rookRow = move.startRow
                    rookStartCol = 7
                    rookEndCol = 5
                    rookPiece = self.board[rookRow][rookEndCol]  # Store rook piece
                    self.board[rookRow][rookStartCol] = rookPiece
                    self.board[rookRow][rookEndCol] = "--"
                else:  # Queen-side castle
                    # Move rook back
                    rookRow = move.startRow
                    rookStartCol = 0
                    rookEndCol = 3
                    rookPiece = self.board[rookRow][rookEndCol]  # Store rook piece
                    self.board[rookRow][rookStartCol] = rookPiece
                    self.board[rookRow][rookEndCol] = "--"
            
            # Restore castling rights
            self.restoreCastlingRights(move)

    def restoreCastlingRights(self, move):
        """Restore castling rights when undoing a move"""
        # If king was moved back, restore castling rights for that color
        if move.pieceMoved[1] == "K":
            if move.pieceMoved[0] == "w":
                # Check if king is back in original position
                if move.startRow == 7 and move.startCol == 4:
                    self.castlingRights[0] = True  # wK
                    self.castlingRights[1] = True  # wQ
            else:
                # Check if king is back in original position
                if move.startRow == 0 and move.startCol == 4:
                    self.castlingRights[2] = True  # bK
                    self.castlingRights[3] = True  # bQ
        
        # If rook was moved back, restore castling rights for that side
        elif move.pieceMoved[1] == "R":
            if move.pieceMoved[0] == "w":
                if move.startCol == 7:  # King-side rook back in position
                    self.castlingRights[0] = True  # wK
                elif move.startCol == 0:  # Queen-side rook back in position
                    self.castlingRights[1] = True  # wQ
            else:
                if move.startCol == 7:  # King-side rook back in position
                    self.castlingRights[2] = True  # bK
                elif move.startCol == 0:  # Queen-side rook back in position
                    self.castlingRights[3] = True  # bQ
        
        # If rook was captured and restored, restore castling rights for that side
        if move.pieceCaptured[1] == "R":
            if move.pieceCaptured[0] == "w":
                if move.endCol == 7:  # King-side rook restored
                    self.castlingRights[0] = True  # wK
                elif move.endCol == 0:  # Queen-side rook restored
                    self.castlingRights[1] = True  # wQ
            else:
                if move.endCol == 7:  # King-side rook restored
                    self.castlingRights[2] = True  # bK
                elif move.endCol == 0:  # Queen-side rook restored
                    self.castlingRights[3] = True  # bQ

    def resetGame(self):
        """Reset the game to the original starting position"""
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.whiteToMove = True
        self.moveLog = []
        # Restore all castling rights
        self.castlingRights = [True, True, True, True]
        # Reset game end state
        self.gameEnded = False
        self.winner = None

    def getValidMoves(self):
        return self.getAllPossibleMoves()
    
    def isValidMove(self, move):
        for m in self.getAllPossibleMoves():
            if (move.startRow == m.startRow and
                move.startCol == m.startCol and
                move.endRow == m.endRow and
                move.endCol == m.endCol):
                return True
        return False
    
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                if piece == "--":
                    continue
                turn = piece[0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    p = piece[1]
                    if p == "p":
                        self.getPawnMoves(r, c, moves)
                    elif p == "R":
                        self.getRookMoves(r, c, moves)
                    elif p == "N":
                        self.getKnightMoves(r, c, moves)
                    elif p == "B":
                        self.getBishopMoves(r, c, moves)
                    elif p == "Q":
                        self.getQueenMoves(r, c, moves)
                    elif p == "K":
                        self.getKingMoves(r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        color = self.board[r][c][0]
        direction = -1 if color == "w" else 1
        startRow = 6 if color == "w" else 1
        # one forward
        if 0 <= r + direction < 8 and self.board[r + direction][c] == "--":
            moves.append(Move((r, c), (r + direction, c), self.board))
            # two forward from start
            if r == startRow and self.board[r + 2 * direction][c] == "--":
                moves.append(Move((r, c), (r + 2 * direction, c), self.board))
        # captures
        for dc in (-1, 1):
            nr, nc = r + direction, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = self.board[nr][nc]
                if target != "--" and target[0] != color:
                    moves.append(Move((r, c), (nr, nc), self.board))

    def getRookMoves(self, r, c, moves):
        self._slide(r, c, moves, [(-1, 0), (1, 0), (0, -1), (0, 1)])

    def getBishopMoves(self, r, c, moves):
        self._slide(r, c, moves, [(-1, -1), (-1, 1), (1, -1), (1, 1)])

    def getQueenMoves(self, r, c, moves):
        self._slide(r, c, moves, [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)])

    def getKnightMoves(self, r, c, moves):
        color = self.board[r][c][0]
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = self.board[nr][nc]
                if target == "--" or target[0] != color:
                    moves.append(Move((r, c), (nr, nc), self.board))

    def getKingMoves(self, r, c, moves):
        color = self.board[r][c][0]
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board[nr][nc]
                    if target == "--" or target[0] != color:
                        moves.append(Move((r, c), (nr, nc), self.board))
        
        # Add castling moves
        self.getCastleMoves(r, c, moves)
    
    def getCastleMoves(self, r, c, moves):
        if self.inCheck():
            return  # Can't castle while in check
        
        color = self.board[r][c][0]
        kingRow = 7 if color == "w" else 0
        
        # King must be in original position (column 4)
        if c != 4:
            return
        
        # King-side castle
        if (color == "w" and self.castlingRights[0]) or (color == "b" and self.castlingRights[2]):
            if (self.board[kingRow][5] == "--" and 
                self.board[kingRow][6] == "--" and
                self.board[kingRow][7][1] == "R" and
                self.board[kingRow][7][0] == color):
                # Check if squares are not under attack
                if not self.squareUnderAttack(kingRow, 5, color) and not self.squareUnderAttack(kingRow, 6, color):
                    moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))
        
        # Queen-side castle
        if (color == "w" and self.castlingRights[1]) or (color == "b" and self.castlingRights[3]):
            if (self.board[kingRow][1] == "--" and 
                self.board[kingRow][2] == "--" and
                self.board[kingRow][0][1] == "R" and
                self.board[kingRow][0][0] == color):
                # Check if squares are not under attack
                if not self.squareUnderAttack(kingRow, 1, color) and not self.squareUnderAttack(kingRow, 2, color):
                    moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))
    
    def inCheck(self):
        # Find the king
        kingRow, kingCol = -1, -1
        kingColor = "w" if self.whiteToMove else "b"
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == kingColor + "K":
                    kingRow, kingCol = r, c
                    break
            if kingRow != -1:
                break
        
        return self.squareUnderAttack(kingRow, kingCol, kingColor)
    
    def squareUnderAttack(self, r, c, defendingColor=None):
        # Check if any opponent piece can attack this square
        if defendingColor is None:
            defendingColor = "w" if self.whiteToMove else "b"
        opponentColor = "b" if defendingColor == "w" else "w"
        
        # Check pawn attacks
        direction = 1 if defendingColor == "w" else -1
        for dc in (-1, 1):
            nr, nc = r - direction, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if self.board[nr][nc] == opponentColor + "p":
                    return True
        
        # Check knight attacks
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if self.board[nr][nc] == opponentColor + "N":
                    return True
        
        # Check sliding pieces (rook, bishop, queen)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                piece = self.board[nr][nc]
                if piece != "--":
                    if piece[0] == opponentColor:
                        if piece[1] == "Q":
                            return True
                        elif piece[1] == "R" and dr * dc == 0:  # Rook moves horizontally/vertically
                            return True
                        elif piece[1] == "B" and dr * dc != 0:  # Bishop moves diagonally
                            return True
                    break
                nr += dr
                nc += dc
        
        # Check king attacks
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if self.board[nr][nc] == opponentColor + "K":
                        return True
        
        return False

    def _slide(self, r, c, moves, directions):
        color = self.board[r][c][0]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = self.board[nr][nc]
                if target == "--":
                    moves.append(Move((r, c), (nr, nc), self.board))
                else:
                    if target[0] != color:
                        moves.append(Move((r, c), (nr, nc), self.board))
                    break
                nr += dr
                nc += dc

class Move():
    #maps keys to values
    #key : value
    #key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[startSq[0]][startSq[1]]
        self.pieceCaptured = board[endSq[0]][endSq[1]]
        self.isCastleMove = isCastleMove

    def getChessNotation(self):
        if self.isCastleMove:
            if self.endCol - self.startCol == 2:
                return "O-O"  # King-side castle
            else:
                return "O-O-O"  # Queen-side castle
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
         
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
        
        