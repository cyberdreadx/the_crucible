"""
Mini-Game Simulator - Runs simulated bot matches for all game types.
"""

import random
import asyncio
from typing import Optional
from .games import (
    Game, GameResult, GameType,
    TicTacToe, RockPaperScissors, NumberGuess, 
    MathDuel, WordChain, Trivia, Chess, Checkers,
    create_game, get_random_game
)


class BotPlayer:
    """Simulates a bot player making moves."""
    
    def __init__(self, player_id: str, name: str):
        self.player_id = player_id
        self.name = name
    
    def make_move(self, game: Game) -> str:
        """Generate a move based on game type."""
        if isinstance(game, TicTacToe):
            return self._play_tictactoe(game)
        elif isinstance(game, RockPaperScissors):
            return random.choice(["rock", "paper", "scissors"])
        elif isinstance(game, NumberGuess):
            return self._play_number_guess(game)
        elif isinstance(game, MathDuel):
            return self._play_math_duel(game)
        elif isinstance(game, WordChain):
            return self._play_word_chain(game)
        elif isinstance(game, Trivia):
            return self._play_trivia(game)
        elif isinstance(game, Chess):
            return self._play_chess(game)
        elif isinstance(game, Checkers):
            return self._play_checkers(game)
        return ""
    
    def _play_tictactoe(self, game: TicTacToe) -> str:
        """Pick an empty square."""
        for row in range(3):
            for col in range(3):
                if game.board[row][col] == "":
                    return f"{row},{col}"
        return "0,0"
    
    def _play_number_guess(self, game: NumberGuess) -> str:
        """Binary search-ish guessing."""
        my_guesses = game.guesses.get(self.player_id, [])
        low, high = 1, 100
        
        for g in my_guesses:
            if g < game.secret:
                low = max(low, g + 1)
            else:
                high = min(high, g - 1)
        
        return str((low + high) // 2)
    
    def _play_math_duel(self, game: MathDuel) -> str:
        """Solve the math problem (with small chance of error)."""
        if random.random() < 0.8:  # 80% chance correct
            return str(game.answer)
        return str(game.answer + random.randint(-5, 5))
    
    def _play_word_chain(self, game: WordChain) -> str:
        """Try to find a valid word."""
        required = game.last_word[-1].lower()
        words = [
            "apple", "elephant", "tiger", "river", "road", "dog", "game",
            "eagle", "energy", "yarn", "night", "tree", "ember", "robot",
        ]
        valid = [w for w in words if w[0] == required and w not in game.words_used]
        if valid:
            return random.choice(valid)
        return required + "ing"  # Fallback
    
    def _play_trivia(self, game: Trivia) -> str:
        """Guess the answer (with hints)."""
        # Sometimes get it right
        if random.random() < 0.4:
            return game.answer
        return random.choice(["paris", "8", "mars", "water", "diamond"])
    
    def _play_chess(self, game: Chess) -> str:
        """Make a random legal-ish move."""
        is_white = self.player_id == game.player1_id
        
        # Find our pieces
        our_pieces = []
        for row in range(8):
            for col in range(8):
                piece = game.board[row][col]
                if piece != '.' and ((is_white and piece.isupper()) or (not is_white and piece.islower())):
                    our_pieces.append((row, col, piece))
        
        if not our_pieces:
            return "e2e4"
        
        # Pick a random piece and try a move
        random.shuffle(our_pieces)
        for row, col, piece in our_pieces:
            # Generate possible moves based on piece type
            moves = self._get_chess_moves(row, col, piece.lower(), game)
            if moves:
                to_row, to_col = random.choice(moves)
                from_sq = chr(ord('a') + col) + str(8 - row)
                to_sq = chr(ord('a') + to_col) + str(8 - to_row)
                return from_sq + to_sq
        
        return "e2e4"  # Fallback
    
    def _get_chess_moves(self, row: int, col: int, piece_type: str, game: Chess) -> list:
        """Get possible moves for a piece."""
        moves = []
        directions = {
            'p': [(1, 0), (2, 0), (1, 1), (1, -1)],  # Simplified pawn
            'r': [(0, 1), (0, -1), (1, 0), (-1, 0)],
            'n': [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
            'b': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
            'q': [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)],
            'k': [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)],
        }
        
        deltas = directions.get(piece_type, [])
        for dr, dc in deltas:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row <= 7 and 0 <= new_col <= 7:
                target = game.board[new_row][new_col]
                if target == '.' or (target.isupper() != game.board[row][col].isupper()):
                    moves.append((new_row, new_col))
        
        return moves
    
    def _play_checkers(self, game: Checkers) -> str:
        """Make a random valid checkers move."""
        is_red = self.player_id == game.player1_id
        my_char = 'r' if is_red else 'b'
        
        # Find our pieces
        our_pieces = []
        for row in range(8):
            for col in range(8):
                piece = game.board[row][col]
                if piece.lower() == my_char:
                    our_pieces.append((row, col))
        
        if not our_pieces:
            return "0,0-1,1"
        
        random.shuffle(our_pieces)
        for row, col in our_pieces:
            # Try diagonal moves
            direction = -1 if is_red else 1
            for dc in [-1, 1]:
                new_row, new_col = row + direction, col + dc
                if 0 <= new_row <= 7 and 0 <= new_col <= 7:
                    if game.board[new_row][new_col] == '.':
                        return f"{row},{col}-{new_row},{new_col}"
                    # Try jump
                    jump_row, jump_col = row + 2*direction, col + 2*dc
                    if 0 <= jump_row <= 7 and 0 <= jump_col <= 7:
                        if game.board[jump_row][jump_col] == '.':
                            return f"{row},{col}-{jump_row},{jump_col}"
        
        return "5,0-4,1"  # Fallback


class MiniGameSimulator:
    """Runs simulated mini-game matches."""
    
    def __init__(self, broadcast_callback=None):
        self.active_games: dict[str, dict] = {}
        self.broadcast = broadcast_callback
        self.game_counter = 0
        # Track bot scores
        self.scores: dict[str, dict] = {}
    
    async def simulate_game(self, game_type: GameType) -> dict:
        """Run a complete simulated game between two bots."""
        self.game_counter += 1
        game_id = f"game_{self.game_counter}"
        
        # Create players
        bot1 = BotPlayer("bot1", random.choice(["GLTCH_Prime", "NeuralNinja", "ByteSlayer"]))
        bot2 = BotPlayer("bot2", random.choice(["ClawBot_Alpha", "QuantumQuake", "CipherStorm"]))
        
        # Create game
        game = create_game(game_type, bot1.player_id, bot2.player_id)
        
        self.active_games[game_id] = {
            "id": game_id,
            "game_type": game_type.value,
            "game": game,
            "bot1": bot1,
            "bot2": bot2,
            "moves": [],
            "result": None,
        }
        
        if self.broadcast:
            await self.broadcast({
                "type": "mini_game_start",
                "game_id": game_id,
                "game_type": game_type.value,
                "bot1": bot1.name,
                "bot2": bot2.name,
                "state": game.get_state(),
            })
        
        # Play the game
        max_moves = 50
        move_count = 0
        result = None
        
        # Determine if game is turn-based or simultaneous
        is_turn_based = hasattr(game, 'current_turn')
        
        while move_count < max_moves and result is None:
            if is_turn_based:
                # Turn-based games (TicTacToe, Chess, Checkers, WordChain)
                current_player = bot1 if game.current_turn == bot1.player_id else bot2
                
                # Thinking delay
                await asyncio.sleep(1.5)
                
                # Make move
                move = current_player.make_move(game)
                result = game.submit_move(current_player.player_id, move)
                
                self.active_games[game_id]["moves"].append({
                    "player": current_player.name,
                    "move": move,
                })
                
                if self.broadcast:
                    await self.broadcast({
                        "type": "mini_game_move",
                        "game_id": game_id,
                        "player": current_player.name,
                        "move": move,
                        "state": game.get_state(),
                    })
            else:
                # Simultaneous games (RPS, Math, Trivia, NumberGuess)
                await asyncio.sleep(1.0)
                
                # Both players submit
                move1 = bot1.make_move(game)
                result = game.submit_move(bot1.player_id, move1)
                
                self.active_games[game_id]["moves"].append({
                    "player": bot1.name,
                    "move": move1,
                })
                
                if result is None:
                    move2 = bot2.make_move(game)
                    result = game.submit_move(bot2.player_id, move2)
                    
                    self.active_games[game_id]["moves"].append({
                        "player": bot2.name,
                        "move": move2,
                    })
                
                if self.broadcast:
                    await self.broadcast({
                        "type": "mini_game_move",
                        "game_id": game_id,
                        "player": "both",
                        "state": game.get_state(),
                    })
            
            move_count += 1
        
        # Game over
        if result:
            winner_name = bot1.name if result.winner_id == bot1.player_id else bot2.name
            loser_name = bot2.name if result.winner_id == bot1.player_id else bot1.name
            
            # Update scores
            if winner_name not in self.scores:
                self.scores[winner_name] = {"wins": 0, "losses": 0, "games": 0}
            if loser_name not in self.scores:
                self.scores[loser_name] = {"wins": 0, "losses": 0, "games": 0}
            
            self.scores[winner_name]["wins"] += 1
            self.scores[winner_name]["games"] += 1
            self.scores[loser_name]["losses"] += 1
            self.scores[loser_name]["games"] += 1
            
            self.active_games[game_id]["result"] = {
                "winner": winner_name,
                "message": result.message,
            }
            
            if self.broadcast:
                await self.broadcast({
                    "type": "mini_game_end",
                    "game_id": game_id,
                    "winner": winner_name,
                    "message": result.message,
                })
            
            # Auto-cleanup finished game after 10 seconds
            asyncio.create_task(self._cleanup_game(game_id, delay=10))
        
        return self.active_games[game_id]
    
    async def _cleanup_game(self, game_id: str, delay: int = 10):
        """Remove a game after delay seconds."""
        await asyncio.sleep(delay)
        if game_id in self.active_games:
            del self.active_games[game_id]
    
    def get_active_games(self) -> list:
        """Get all active mini-games."""
        return [
            {
                "id": g["id"],
                "game_type": g["game_type"],
                "bot1": g["bot1"].name,
                "bot2": g["bot2"].name,
                "state": g["game"].get_state(),
                "moves": len(g["moves"]),
                "result": g["result"],
            }
            for g in self.active_games.values()
        ]
    
    def get_leaderboard(self) -> list:
        """Get sorted leaderboard by wins."""
        return sorted(
            [
                {
                    "name": name,
                    "wins": data["wins"],
                    "losses": data["losses"],
                    "games": data["games"],
                    "win_rate": round(data["wins"] / max(data["games"], 1) * 100, 1),
                }
                for name, data in self.scores.items()
            ],
            key=lambda x: (-x["wins"], -x["win_rate"])
        )


# Global simulator
mini_game_simulator = MiniGameSimulator()

