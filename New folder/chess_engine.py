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

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #to undo moves later on 
        self.whiteToMove = not self.whiteToMove #swap btw players

            
        
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove


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

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[startSq[0]][startSq[1]]
        self.pieceCaptured = board[endSq[0]][endSq[1]]

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
         
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
        
        