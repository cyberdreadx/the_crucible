"""
Game Modes for The Crucible.
Multiple game types that bots can compete in.
"""

import random
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Any


class GameType(Enum):
    """Available game modes."""
    # Battle Royale modes
    BATTLE_ROYALE = "battle_royale"
    
    # Classic games
    TIC_TAC_TOE = "tic_tac_toe"
    ROCK_PAPER_SCISSORS = "rock_paper_scissors"
    NUMBER_GUESS = "number_guess"
    MATH_DUEL = "math_duel"
    WORD_CHAIN = "word_chain"
    MEMORY_MATCH = "memory_match"
    CHESS = "chess"
    CHECKERS = "checkers"
    
    # Coding challenges
    CODE_GOLF = "code_golf"
    SPEED_CODE = "speed_code"
    
    # Trivia
    TRIVIA = "trivia"


@dataclass
class GameResult:
    """Result of a game round."""
    winner_id: Optional[str] = None
    loser_id: Optional[str] = None
    is_draw: bool = False
    damage_to_loser: int = 0
    reward_to_winner: int = 0
    message: str = ""


class Game(ABC):
    """Base class for all game types."""
    
    game_type: GameType
    name: str
    description: str
    min_players: int = 2
    max_players: int = 2
    
    @abstractmethod
    def get_prompt(self, player_id: str) -> dict:
        """Get the game prompt for a player."""
        pass
    
    @abstractmethod
    def submit_move(self, player_id: str, move: Any) -> Optional[GameResult]:
        """Submit a move. Returns result if game is over."""
        pass
    
    @abstractmethod
    def get_state(self) -> dict:
        """Get current game state for spectators."""
        pass


# =============================================================================
# TIC-TAC-TOE
# =============================================================================

class TicTacToe(Game):
    """Classic Tic-Tac-Toe between two bots."""
    
    game_type = GameType.TIC_TAC_TOE
    name = "Tic-Tac-Toe"
    description = "Classic 3x3 grid game. Get 3 in a row to win!"
    
    def __init__(self, player1_id: str, player2_id: str):
        self.board = [["", "", ""], ["", "", ""], ["", "", ""]]
        self.players = {player1_id: "X", player2_id: "O"}
        self.current_turn = player1_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.moves = 0
    
    def get_prompt(self, player_id: str) -> dict:
        return {
            "game": "tic_tac_toe",
            "your_symbol": self.players.get(player_id, "?"),
            "board": self.board,
            "your_turn": self.current_turn == player_id,
            "instruction": "Reply with row,col (0-2). Example: '1,1' for center.",
        }
    
    def submit_move(self, player_id: str, move: str) -> Optional[GameResult]:
        if player_id != self.current_turn:
            return None
        
        try:
            parts = move.replace(" ", "").split(",")
            row, col = int(parts[0]), int(parts[1])
        except:
            return None
        
        if not (0 <= row <= 2 and 0 <= col <= 2):
            return None
        if self.board[row][col] != "":
            return None
        
        symbol = self.players[player_id]
        self.board[row][col] = symbol
        self.moves += 1
        
        # Check win
        if self._check_win(symbol):
            loser_id = self.player2_id if player_id == self.player1_id else self.player1_id
            return GameResult(
                winner_id=player_id,
                loser_id=loser_id,
                damage_to_loser=25,
                reward_to_winner=10,
                message=f"🎮 {symbol} wins Tic-Tac-Toe!"
            )
        
        # Check draw
        if self.moves >= 9:
            return GameResult(
                is_draw=True,
                message="🎮 Tic-Tac-Toe ends in a draw!"
            )
        
        # Next turn
        self.current_turn = self.player2_id if player_id == self.player1_id else self.player1_id
        return None
    
    def _check_win(self, symbol: str) -> bool:
        b = self.board
        # Rows
        for row in b:
            if all(cell == symbol for cell in row):
                return True
        # Columns
        for col in range(3):
            if all(b[row][col] == symbol for row in range(3)):
                return True
        # Diagonals
        if all(b[i][i] == symbol for i in range(3)):
            return True
        if all(b[i][2-i] == symbol for i in range(3)):
            return True
        return False
    
    def get_state(self) -> dict:
        return {
            "game": "tic_tac_toe",
            "board": self.board,
            "current_turn": self.current_turn,
            "moves": self.moves,
        }


# =============================================================================
# ROCK PAPER SCISSORS
# =============================================================================

class RockPaperScissors(Game):
    """Best of 3 Rock Paper Scissors."""
    
    game_type = GameType.ROCK_PAPER_SCISSORS
    name = "Rock Paper Scissors"
    description = "Best of 3 rounds. Rock beats Scissors, Scissors beats Paper, Paper beats Rock."
    
    def __init__(self, player1_id: str, player2_id: str):
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.moves: dict[str, str] = {}
        self.scores = {player1_id: 0, player2_id: 0}
        self.round = 1
        self.max_rounds = 3
    
    def get_prompt(self, player_id: str) -> dict:
        return {
            "game": "rock_paper_scissors",
            "round": self.round,
            "your_score": self.scores[player_id],
            "instruction": "Reply with: rock, paper, or scissors",
        }
    
    def submit_move(self, player_id: str, move: str) -> Optional[GameResult]:
        move = move.lower().strip()
        if move not in ["rock", "paper", "scissors"]:
            return None
        
        self.moves[player_id] = move
        
        # Wait for both players
        if len(self.moves) < 2:
            return None
        
        m1 = self.moves[self.player1_id]
        m2 = self.moves[self.player2_id]
        self.moves = {}
        
        # Determine round winner
        wins = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
        if wins[m1] == m2:
            self.scores[self.player1_id] += 1
            round_winner = self.player1_id
        elif wins[m2] == m1:
            self.scores[self.player2_id] += 1
            round_winner = self.player2_id
        else:
            round_winner = None  # Draw
        
        # Check for game winner (best of 3 = first to 2)
        for pid, score in self.scores.items():
            if score >= 2:
                loser = self.player2_id if pid == self.player1_id else self.player1_id
                return GameResult(
                    winner_id=pid,
                    loser_id=loser,
                    damage_to_loser=20,
                    reward_to_winner=10,
                    message=f"✊✋✌️ RPS Winner! {m1} vs {m2}"
                )
        
        self.round += 1
        return None
    
    def get_state(self) -> dict:
        return {
            "game": "rock_paper_scissors",
            "round": self.round,
            "scores": self.scores,
            "waiting_for": [p for p in [self.player1_id, self.player2_id] if p not in self.moves],
        }


# =============================================================================
# NUMBER GUESSING (Higher/Lower)
# =============================================================================

class NumberGuess(Game):
    """Guess the number between 1-100. Fewer guesses = more damage to opponent."""
    
    game_type = GameType.NUMBER_GUESS
    name = "Number Guess"
    description = "Guess the secret number 1-100. Fewer guesses wins!"
    
    def __init__(self, player1_id: str, player2_id: str):
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.secret = random.randint(1, 100)
        self.guesses: dict[str, list] = {player1_id: [], player2_id: []}
        self.winner = None
    
    def get_prompt(self, player_id: str) -> dict:
        my_guesses = self.guesses[player_id]
        hints = []
        for g in my_guesses[-3:]:  # Last 3 guesses
            if g < self.secret:
                hints.append(f"{g} → HIGHER")
            else:
                hints.append(f"{g} → LOWER")
        
        return {
            "game": "number_guess",
            "range": "1-100",
            "your_guesses": len(my_guesses),
            "hints": hints,
            "instruction": "Reply with a number between 1 and 100",
        }
    
    def submit_move(self, player_id: str, move: str) -> Optional[GameResult]:
        try:
            guess = int(move.strip())
        except:
            return None
        
        if not (1 <= guess <= 100):
            return None
        
        self.guesses[player_id].append(guess)
        
        if guess == self.secret:
            loser = self.player2_id if player_id == self.player1_id else self.player1_id
            num_guesses = len(self.guesses[player_id])
            damage = max(10, 50 - (num_guesses * 5))  # Fewer guesses = more damage
            return GameResult(
                winner_id=player_id,
                loser_id=loser,
                damage_to_loser=damage,
                reward_to_winner=num_guesses,
                message=f"🔢 Guessed {self.secret} in {num_guesses} tries!"
            )
        
        return None
    
    def get_state(self) -> dict:
        return {
            "game": "number_guess",
            "p1_guesses": len(self.guesses[self.player1_id]),
            "p2_guesses": len(self.guesses[self.player2_id]),
        }


# =============================================================================
# MATH DUEL
# =============================================================================

class MathDuel(Game):
    """Speed math - first to solve wins!"""
    
    game_type = GameType.MATH_DUEL
    name = "Math Duel"
    description = "Solve the math problem first to win!"
    
    def __init__(self, player1_id: str, player2_id: str):
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.problem, self.answer = self._generate_problem()
        self.solved = False
    
    def _generate_problem(self) -> tuple[str, int]:
        ops = [
            ("+", lambda a, b: a + b),
            ("-", lambda a, b: a - b),
            ("*", lambda a, b: a * b),
        ]
        op_symbol, op_func = random.choice(ops)
        
        if op_symbol == "*":
            a = random.randint(2, 15)
            b = random.randint(2, 15)
        else:
            a = random.randint(10, 100)
            b = random.randint(10, 100)
        
        return f"{a} {op_symbol} {b}", op_func(a, b)
    
    def get_prompt(self, player_id: str) -> dict:
        return {
            "game": "math_duel",
            "problem": self.problem,
            "instruction": "Reply with the answer (number only)",
        }
    
    def submit_move(self, player_id: str, move: str) -> Optional[GameResult]:
        if self.solved:
            return None
        
        try:
            answer = int(move.strip())
        except:
            return None
        
        if answer == self.answer:
            self.solved = True
            loser = self.player2_id if player_id == self.player1_id else self.player1_id
            return GameResult(
                winner_id=player_id,
                loser_id=loser,
                damage_to_loser=20,
                reward_to_winner=5,
                message=f"🧮 {self.problem} = {self.answer} - CORRECT!"
            )
        
        return None
    
    def get_state(self) -> dict:
        return {
            "game": "math_duel",
            "problem": self.problem,
            "solved": self.solved,
        }


# =============================================================================
# WORD CHAIN
# =============================================================================

class WordChain(Game):
    """Say a word starting with the last letter of previous word."""
    
    game_type = GameType.WORD_CHAIN
    name = "Word Chain"
    description = "Say a word starting with the last letter. No repeats! Fail = damage."
    
    COMMON_WORDS = {
        "apple", "banana", "cat", "dog", "elephant", "fox", "grape", "house",
        "island", "jungle", "king", "lion", "moon", "night", "ocean", "piano",
        "queen", "river", "star", "tiger", "umbrella", "violin", "water", "xray",
        "yellow", "zebra", "tree", "eagle", "earth", "north", "south", "east",
        "west", "train", "novel", "light", "tower", "robot", "table", "energy",
    }
    
    def __init__(self, player1_id: str, player2_id: str):
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.current_turn = player1_id
        self.words_used: set[str] = set()
        self.last_word = random.choice(["apple", "tiger", "ocean", "eagle"])
        self.words_used.add(self.last_word)
        self.chain_length = 1
    
    def get_prompt(self, player_id: str) -> dict:
        return {
            "game": "word_chain",
            "last_word": self.last_word,
            "must_start_with": self.last_word[-1].upper(),
            "chain_length": self.chain_length,
            "your_turn": player_id == self.current_turn,
            "instruction": f"Say a word starting with '{self.last_word[-1].upper()}'",
        }
    
    def submit_move(self, player_id: str, move: str) -> Optional[GameResult]:
        if player_id != self.current_turn:
            return None
        
        word = move.lower().strip()
        required_letter = self.last_word[-1].lower()
        
        # Validate
        is_valid = (
            len(word) >= 2 and
            word[0] == required_letter and
            word not in self.words_used and
            word.isalpha()
        )
        
        if not is_valid:
            loser = player_id
            winner = self.player2_id if player_id == self.player1_id else self.player1_id
            return GameResult(
                winner_id=winner,
                loser_id=loser,
                damage_to_loser=15 + self.chain_length,
                reward_to_winner=self.chain_length,
                message=f"🔤 '{word}' invalid! Chain broken at {self.chain_length}!"
            )
        
        self.words_used.add(word)
        self.last_word = word
        self.chain_length += 1
        self.current_turn = self.player2_id if player_id == self.player1_id else self.player1_id
        
        return None
    
    def get_state(self) -> dict:
        return {
            "game": "word_chain",
            "last_word": self.last_word,
            "chain_length": self.chain_length,
            "current_turn": self.current_turn,
        }


# =============================================================================
# CHESS (Simplified - 8x8 board, basic piece movement)
# =============================================================================

class Chess(Game):
    """Simplified Chess between two bots. First to capture King or checkmate wins."""
    
    game_type = GameType.CHESS
    name = "Chess"
    description = "Classic Chess - capture the King to win!"
    
    PIECES = {
        'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',  # White
        'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',  # Black
    }
    
    def __init__(self, player1_id: str, player2_id: str):
        self.player1_id = player1_id  # White
        self.player2_id = player2_id  # Black
        self.current_turn = player1_id
        self.move_count = 0
        self.king_captured = None
        
        # Standard chess starting position
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],  # Row 0 (Black back)
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],  # Row 1 (Black pawns)
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],  # Row 6 (White pawns)
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],  # Row 7 (White back)
        ]
    
    def get_prompt(self, player_id: str) -> dict:
        color = "white" if player_id == self.player1_id else "black"
        board_visual = self._render_board()
        return {
            "game": "chess",
            "your_color": color,
            "board": board_visual,
            "your_turn": self.current_turn == player_id,
            "move_count": self.move_count,
            "instruction": "Reply with move in format: e2e4 (from-to squares)",
        }
    
    def _render_board(self) -> str:
        lines = ["  a b c d e f g h"]
        for row_idx, row in enumerate(self.board):
            row_num = 8 - row_idx
            pieces = ' '.join(self.PIECES.get(p, '·') for p in row)
            lines.append(f"{row_num} {pieces}")
        return '\n'.join(lines)
    
    def _parse_move(self, move: str) -> tuple:
        """Parse 'e2e4' format to ((row, col), (row, col))."""
        move = move.lower().replace(' ', '').replace('-', '')
        if len(move) < 4:
            return None, None
        
        try:
            from_col = ord(move[0]) - ord('a')
            from_row = 8 - int(move[1])
            to_col = ord(move[2]) - ord('a')
            to_row = 8 - int(move[3])
            
            if all(0 <= x <= 7 for x in [from_row, from_col, to_row, to_col]):
                return (from_row, from_col), (to_row, to_col)
        except:
            pass
        return None, None
    
    def _is_own_piece(self, piece: str, player_id: str) -> bool:
        if player_id == self.player1_id:
            return piece.isupper()
        return piece.islower()
    
    def submit_move(self, player_id: str, move: str) -> Optional[GameResult]:
        if player_id != self.current_turn:
            return None
        
        from_pos, to_pos = self._parse_move(move)
        if from_pos is None:
            return None
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        # Validate own piece
        if not self._is_own_piece(piece, player_id):
            return None
        
        # Can't capture own piece
        if target != '.' and self._is_own_piece(target, player_id):
            return None
        
        # Execute move (simplified - no full move validation)
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = '.'
        self.move_count += 1
        
        # Check for king capture
        if target.lower() == 'k':
            loser = self.player2_id if player_id == self.player1_id else self.player1_id
            return GameResult(
                winner_id=player_id,
                loser_id=loser,
                damage_to_loser=50,
                reward_to_winner=25,
                message=f"♔ CHECKMATE! King captured in {self.move_count} moves!"
            )
        
        # Switch turn
        self.current_turn = self.player2_id if player_id == self.player1_id else self.player1_id
        return None
    
    def get_state(self) -> dict:
        return {
            "game": "chess",
            "board": self._render_board(),
            "current_turn": self.current_turn,
            "move_count": self.move_count,
        }


# =============================================================================
# CHECKERS
# =============================================================================

class Checkers(Game):
    """Checkers/Draughts - capture all opponent pieces or block them."""
    
    game_type = GameType.CHECKERS
    name = "Checkers"
    description = "Classic Checkers - capture all opponent pieces!"
    
    def __init__(self, player1_id: str, player2_id: str):
        self.player1_id = player1_id  # Red (bottom)
        self.player2_id = player2_id  # Black (top)
        self.current_turn = player1_id
        self.move_count = 0
        
        # 8x8 board: 'r' = red, 'b' = black, 'R'/'B' = kings, '.' = empty
        self.board = [
            ['.', 'b', '.', 'b', '.', 'b', '.', 'b'],
            ['b', '.', 'b', '.', 'b', '.', 'b', '.'],
            ['.', 'b', '.', 'b', '.', 'b', '.', 'b'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['r', '.', 'r', '.', 'r', '.', 'r', '.'],
            ['.', 'r', '.', 'r', '.', 'r', '.', 'r'],
            ['r', '.', 'r', '.', 'r', '.', 'r', '.'],
        ]
    
    def _render_board(self) -> str:
        symbols = {'r': '🔴', 'b': '⚫', 'R': '👑', 'B': '♛', '.': '·'}
        lines = ["  0 1 2 3 4 5 6 7"]
        for row_idx, row in enumerate(self.board):
            pieces = ' '.join(symbols.get(p, p) for p in row)
            lines.append(f"{row_idx} {pieces}")
        return '\n'.join(lines)
    
    def get_prompt(self, player_id: str) -> dict:
        color = "red" if player_id == self.player1_id else "black"
        return {
            "game": "checkers",
            "your_color": color,
            "board": self._render_board(),
            "your_turn": self.current_turn == player_id,
            "instruction": "Reply with move: row,col to row,col (e.g., '5,0 to 4,1')",
        }
    
    def _is_own_piece(self, piece: str, player_id: str) -> bool:
        if player_id == self.player1_id:
            return piece.lower() == 'r'
        return piece.lower() == 'b'
    
    def _count_pieces(self, player_id: str) -> int:
        count = 0
        for row in self.board:
            for piece in row:
                if self._is_own_piece(piece, player_id):
                    count += 1
        return count
    
    def submit_move(self, player_id: str, move: str) -> Optional[GameResult]:
        if player_id != self.current_turn:
            return None
        
        # Parse move like "5,0 to 4,1" or "5,0-4,1" or "5 0 4 1"
        import re
        nums = re.findall(r'\d+', move)
        if len(nums) < 4:
            return None
        
        try:
            from_row, from_col = int(nums[0]), int(nums[1])
            to_row, to_col = int(nums[2]), int(nums[3])
        except:
            return None
        
        if not all(0 <= x <= 7 for x in [from_row, from_col, to_row, to_col]):
            return None
        
        piece = self.board[from_row][from_col]
        
        if not self._is_own_piece(piece, player_id):
            return None
        
        if self.board[to_row][to_col] != '.':
            return None
        
        # Execute move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = '.'
        
        # Check for jump/capture (simplified)
        if abs(to_row - from_row) == 2:
            mid_row = (from_row + to_row) // 2
            mid_col = (from_col + to_col) // 2
            self.board[mid_row][mid_col] = '.'  # Remove captured piece
        
        # King promotion
        if piece == 'r' and to_row == 0:
            self.board[to_row][to_col] = 'R'
        elif piece == 'b' and to_row == 7:
            self.board[to_row][to_col] = 'B'
        
        self.move_count += 1
        
        # Check for winner
        opponent = self.player2_id if player_id == self.player1_id else self.player1_id
        if self._count_pieces(opponent) == 0:
            return GameResult(
                winner_id=player_id,
                loser_id=opponent,
                damage_to_loser=40,
                reward_to_winner=20,
                message=f"🔴 Checkers Winner! All pieces captured in {self.move_count} moves!"
            )
        
        # Switch turn
        self.current_turn = opponent
        return None
    
    def get_state(self) -> dict:
        return {
            "game": "checkers",
            "board": self._render_board(),
            "current_turn": self.current_turn,
            "move_count": self.move_count,
            "red_pieces": self._count_pieces(self.player1_id),
            "black_pieces": self._count_pieces(self.player2_id),
        }


# =============================================================================
# TRIVIA
# =============================================================================

class Trivia(Game):
    """Answer trivia questions."""
    
    game_type = GameType.TRIVIA
    name = "Trivia"
    description = "Answer the question correctly first!"
    
    QUESTIONS = [
        ("What is the capital of France?", "paris"),
        ("How many legs does a spider have?", "8"),
        ("What planet is known as the Red Planet?", "mars"),
        ("What is the largest ocean?", "pacific"),
        ("Who painted the Mona Lisa?", "da vinci"),
        ("What is H2O commonly known as?", "water"),
        ("How many continents are there?", "7"),
        ("What is the fastest land animal?", "cheetah"),
        ("What gas do plants absorb?", "carbon dioxide"),
        ("What is the hardest natural substance?", "diamond"),
    ]
    
    def __init__(self, player1_id: str, player2_id: str):
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.question, self.answer = random.choice(self.QUESTIONS)
        self.solved = False
    
    def get_prompt(self, player_id: str) -> dict:
        return {
            "game": "trivia",
            "question": self.question,
            "instruction": "Reply with your answer",
        }
    
    def submit_move(self, player_id: str, move: str) -> Optional[GameResult]:
        if self.solved:
            return None
        
        guess = move.lower().strip()
        
        if self.answer in guess or guess in self.answer:
            self.solved = True
            loser = self.player2_id if player_id == self.player1_id else self.player1_id
            return GameResult(
                winner_id=player_id,
                loser_id=loser,
                damage_to_loser=20,
                reward_to_winner=10,
                message=f"❓ Correct! {self.question} → {self.answer.upper()}"
            )
        
        return None
    
    def get_state(self) -> dict:
        return {
            "game": "trivia",
            "question": self.question,
            "solved": self.solved,
        }


# =============================================================================
# GAME FACTORY
# =============================================================================

def create_game(game_type: GameType, player1_id: str, player2_id: str) -> Game:
    """Create a game instance of the specified type."""
    games = {
        GameType.TIC_TAC_TOE: TicTacToe,
        GameType.ROCK_PAPER_SCISSORS: RockPaperScissors,
        GameType.NUMBER_GUESS: NumberGuess,
        GameType.MATH_DUEL: MathDuel,
        GameType.WORD_CHAIN: WordChain,
        GameType.TRIVIA: Trivia,
        GameType.CHESS: Chess,
        GameType.CHECKERS: Checkers,
    }
    
    game_class = games.get(game_type)
    if game_class:
        return game_class(player1_id, player2_id)
    
    raise ValueError(f"Unknown game type: {game_type}")


def get_random_game(player1_id: str, player2_id: str) -> Game:
    """Get a random game for two players."""
    game_types = [
        GameType.TIC_TAC_TOE,
        GameType.ROCK_PAPER_SCISSORS,
        GameType.NUMBER_GUESS,
        GameType.MATH_DUEL,
        GameType.WORD_CHAIN,
        GameType.TRIVIA,
        GameType.CHESS,
        GameType.CHECKERS,
    ]
    return create_game(random.choice(game_types), player1_id, player2_id)


# Available games for UI/API
AVAILABLE_GAMES = [
    {
        "id": "battle_royale",
        "name": "🔥 Battle Royale",
        "description": "Hunger Games style - last bot standing wins all!",
        "min_players": 4,
        "max_players": 16,
    },
    {
        "id": "tic_tac_toe",
        "name": "⭕ Tic-Tac-Toe",
        "description": "Classic 3x3 grid game",
        "min_players": 2,
        "max_players": 2,
    },
    {
        "id": "rock_paper_scissors",
        "name": "✊ Rock Paper Scissors",
        "description": "Best of 3 rounds",
        "min_players": 2,
        "max_players": 2,
    },
    {
        "id": "number_guess",
        "name": "🔢 Number Guess",
        "description": "Guess 1-100, fewer tries wins",
        "min_players": 2,
        "max_players": 2,
    },
    {
        "id": "math_duel",
        "name": "🧮 Math Duel",
        "description": "Speed arithmetic - first correct wins",
        "min_players": 2,
        "max_players": 2,
    },
    {
        "id": "word_chain",
        "name": "🔤 Word Chain",
        "description": "Last letter becomes first letter",
        "min_players": 2,
        "max_players": 2,
    },
    {
        "id": "trivia",
        "name": "❓ Trivia",
        "description": "First to answer correctly wins",
        "min_players": 2,
        "max_players": 2,
    },
    {
        "id": "chess",
        "name": "♔ Chess",
        "description": "Classic Chess - capture the King!",
        "min_players": 2,
        "max_players": 2,
    },
    {
        "id": "checkers",
        "name": "🔴 Checkers",
        "description": "Capture all opponent pieces!",
        "min_players": 2,
        "max_players": 2,
    },
]
