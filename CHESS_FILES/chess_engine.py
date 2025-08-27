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
        # En passant tracking: (row, col) of the square where en passant capture is possible, or None
        self.enPassantSquare = None
        # Game state history for proper undo functionality
        self.gameStateHistory = []  # Stores (castlingRights, enPassantSquare, gameEnded, winner) for each move
        # Game end tracking
        self.gameEnded = False
        self.winner = None  # "White" or "Black"

    def makeMove(self, move):
        # Save current game state for undo
        self.gameStateHistory.append((
            self.castlingRights.copy(),
            self.enPassantSquare,
            self.gameEnded,
            self.winner
        ))

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

        # Handle en passant capture BEFORE moving the pawn
        if move.isEnPassantMove:
            # Remove the captured pawn (which is on the same row as the moving pawn, but different column)
            capturedPawnRow = move.startRow  # Same row as the attacking pawn
            capturedPawnCol = move.endCol    # Same column as the destination (where the captured pawn is)
            self.board[capturedPawnRow][capturedPawnCol] = "--"

        # Check for king capture before making the move
        if move.pieceCaptured[1] == "K":  # King is being captured
            self.gameEnded = True
            # The player making the move wins
            self.winner = "White" if self.whiteToMove else "Black"

        # Now move the piece
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #to undo moves later on
        self.whiteToMove = not self.whiteToMove #swap btw players

        # Update en passant square
        self.updateEnPassantSquare(move)

        # Update castling rights
        self.updateCastlingRights(move)

    def updateEnPassantSquare(self, move):
        """Update the en passant square based on the move made"""
        # Reset en passant square
        self.enPassantSquare = None

        # Check if a pawn moved two squares forward
        if move.pieceMoved[1] == "p" and abs(move.endRow - move.startRow) == 2:
            # Set en passant square to the square the pawn passed over
            enPassantRow = (move.startRow + move.endRow) // 2
            enPassantCol = move.endCol  # Fixed: should be endCol, not startCol
            self.enPassantSquare = (enPassantRow, enPassantCol)

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
        if len(self.moveLog) != 0 and len(self.gameStateHistory) != 0:
            move = self.moveLog.pop()

            # Restore the previous game state
            prevCastlingRights, prevEnPassantSquare, prevGameEnded, prevWinner = self.gameStateHistory.pop()
            self.castlingRights = prevCastlingRights
            self.enPassantSquare = prevEnPassantSquare
            self.gameEnded = prevGameEnded
            self.winner = prevWinner

            # First restore the moving piece
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            # Handle en passant undo (restore the captured pawn)
            if move.isEnPassantMove:
                # For en passant, the captured pawn was on the same row as the moving pawn
                # but in the column where the moving pawn ended up
                capturedPawnRow = move.startRow  # Same row as the attacking pawn
                capturedPawnCol = move.endCol    # Same column as destination
                self.board[capturedPawnRow][capturedPawnCol] = move.pieceCaptured
                # The destination square should be empty after undo (no piece was originally there)
                self.board[move.endRow][move.endCol] = "--"

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
        # Reset en passant
        self.enPassantSquare = None
        # Reset game state history
        self.gameStateHistory = []
        # Reset game end state
        self.gameEnded = False
        self.winner = None

    def getValidMoves(self):
        """Get all valid moves that don't leave the king in check"""
        moves = []
        allPossibleMoves = self.getAllPossibleMoves()

        # Store the current board state to verify integrity
        originalEnPassantSquare = self.enPassantSquare

        for move in allPossibleMoves:
            # Make the move temporarily
            self.makeMove(move)

            # Check if this move leaves our king in check
            # Switch back to check the previous player's king
            self.whiteToMove = not self.whiteToMove
            if not self.inCheck():
                moves.append(move)

            # Switch back and undo the move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        # Verify board integrity - en passant square should be restored
        if self.enPassantSquare != originalEnPassantSquare:
            # Restore the original en passant square if it was corrupted
            self.enPassantSquare = originalEnPassantSquare

        return moves
    
    def isValidMove(self, move):
        """Check if a move is valid (doesn't leave king in check)"""
        validMoves = self.getValidMoves()
        for m in validMoves:
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

        # En passant captures
        if self.enPassantSquare is not None:
            enPassantRow, enPassantCol = self.enPassantSquare
            # Check if this pawn can capture en passant
            # The pawn must be on the correct rank (5th for white, 4th for black)
            # and adjacent to the en passant square column
            correctRank = 3 if color == "w" else 4  # 5th rank for white (index 3), 4th rank for black (index 4)
            if r == correctRank and abs(c - enPassantCol) == 1:
                # The pawn can capture en passant - move to the en passant square
                moves.append(Move((r, c), (enPassantRow, enPassantCol), self.board, isEnPassantMove=True))

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

    def __init__(self, startSq, endSq, board, isCastleMove=False, isEnPassantMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[startSq[0]][startSq[1]]
        self.pieceCaptured = board[endSq[0]][endSq[1]]
        self.isCastleMove = isCastleMove
        self.isEnPassantMove = isEnPassantMove
        # For en passant, we need to track the captured pawn separately
        if isEnPassantMove:
            # The captured pawn is on the same row as the moving pawn, not the destination square
            capturedPawnRow = startSq[0]
            capturedPawnCol = endSq[1]
            self.pieceCaptured = board[capturedPawnRow][capturedPawnCol]

    def getChessNotation(self):
        if self.isCastleMove:
            if self.endCol - self.startCol == 2:
                return "O-O"  # King-side castle
            else:
                return "O-O-O"  # Queen-side castle

        notation = self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
        if self.isEnPassantMove:
            notation += " e.p."  # Add en passant indicator
        return notation
         
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
        
        