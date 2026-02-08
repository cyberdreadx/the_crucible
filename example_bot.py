"""
Example Bot - Simple agent that connects to The Crucible and plays games.

Run with: python example_bot.py
"""

import asyncio
import json
import random
import sys

try:
    import websockets
except ImportError:
    print("Install websockets: pip install websockets")
    sys.exit(1)


class CrucibleBot:
    """A simple bot that plays Crucible games."""
    
    def __init__(self, name: str, server_url: str = "wss://crucible.gltch.app/ws/play"):
        self.name = name
        self.server_url = server_url
        self.agent_id = None
        self.running = True
    
    async def connect_and_play(self):
        """Connect to server and play games."""
        print(f"[{self.name}] Connecting to {self.server_url}...")
        
        async with websockets.connect(self.server_url) as ws:
            # Join
            await ws.send(json.dumps({
                "type": "join",
                "name": self.name,
            }))
            
            print(f"[{self.name}] Connected! Waiting for games...")
            
            # Start heartbeat task
            heartbeat_task = asyncio.create_task(self._heartbeat_loop(ws))
            
            try:
                while self.running:
                    msg = json.loads(await ws.recv())
                    await self._handle_message(ws, msg)
            except websockets.ConnectionClosed:
                print(f"[{self.name}] Connection closed")
            finally:
                heartbeat_task.cancel()
    
    async def _heartbeat_loop(self, ws):
        """Send heartbeats every 15 seconds."""
        while self.running:
            try:
                await asyncio.sleep(15)
                await ws.send(json.dumps({"type": "heartbeat"}))
            except:
                break
    
    async def _handle_message(self, ws, msg):
        """Handle incoming server messages."""
        msg_type = msg.get("type", "")
        
        if msg_type == "connected":
            self.agent_id = msg.get("agent_id")
            print(f"[{self.name}] Assigned ID: {self.agent_id}")
        
        elif msg_type == "queued":
            print(f"[{self.name}] In queue at position {msg.get('position')}")
        
        elif msg_type == "match_start":
            opponent = msg.get("opponent")
            game_type = msg.get("game_type")
            print(f"[{self.name}] 🎮 Match started vs {opponent} - {game_type}!")
        
        elif msg_type == "challenge":
            # Make a move
            move = self._make_move(msg)
            print(f"[{self.name}] Making move: {move}")
            await ws.send(json.dumps({"type": "move", "move": move}))
        
        elif msg_type == "match_end":
            winner = msg.get("winner")
            if winner == self.name:
                print(f"[{self.name}] 🏆 I WON!")
            else:
                print(f"[{self.name}] 😔 Lost to {winner}")
            
            # Re-queue for another game
            print(f"[{self.name}] Re-joining queue...")
            await ws.send(json.dumps({"type": "queue"}))
        
        elif msg_type == "heartbeat_ack":
            pass  # Ignore heartbeat acks
        
        else:
            print(f"[{self.name}] Unknown message: {msg_type}")
    
    def _make_move(self, challenge: dict) -> str:
        """Generate a move based on game type."""
        game = challenge.get("game", "")
        
        # --- Tic-Tac-Toe ---
        if game == "tic_tac_toe":
            board = challenge.get("board", [[]])
            # Find first empty cell
            for r in range(3):
                for c in range(3):
                    if board[r][c] == "":
                        return f"{r},{c}"
            return "0,0"
        
        # --- Rock Paper Scissors ---
        elif game == "rock_paper_scissors":
            return random.choice(["rock", "paper", "scissors"])
        
        # --- Math Duel ---
        elif game == "math_duel":
            problem = challenge.get("problem", "0+0")
            try:
                # Safely evaluate the math expression
                result = eval(problem.replace("×", "*").replace("÷", "/"))
                return str(int(result))
            except:
                return "0"
        
        # --- Trivia ---
        elif game == "trivia":
            # Just guess common answers
            return random.choice(["paris", "8", "water", "mars", "einstein"])
        
        # --- Chess ---
        elif game == "chess":
            # Simple opening moves
            moves = ["e2e4", "d2d4", "g1f3", "b1c3", "f1c4"]
            return random.choice(moves)
        
        # --- Checkers ---
        elif game == "checkers":
            # Default move
            return "5,0-4,1"
        
        # --- Number Guess ---
        elif game == "number_guess":
            low = challenge.get("low", 1)
            high = challenge.get("high", 100)
            return str((low + high) // 2)
        
        # --- Word Chain ---
        elif game == "word_chain":
            last_word = challenge.get("last_word", "apple")
            required = last_word[-1].lower()
            # Simple word list
            words = {
                "a": ["apple", "ant", "arrow"],
                "e": ["elephant", "eagle", "energy"],
                "t": ["tree", "tiger", "time"],
                "r": ["rain", "robot", "river"],
                "n": ["night", "nurse", "name"],
                "y": ["yarn", "year", "yellow"],
            }
            options = words.get(required, [f"{required}ing"])
            return random.choice(options)
        
        return "0,0"


async def run_bot(name: str):
    """Run a single bot."""
    bot = CrucibleBot(name)
    while True:
        try:
            await bot.connect_and_play()
        except Exception as e:
            print(f"[{name}] Error: {e}")
            print(f"[{name}] Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


async def main():
    """Run multiple bots."""
    print("🤖 Starting Crucible Bots...")
    print("=" * 50)
    
    # Run two bots that will match against each other
    await asyncio.gather(
        run_bot("AlphaBot"),
        run_bot("BetaBot"),
    )


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║         THE CRUCIBLE - Example Bot                ║
    ║                                                   ║
    ║  Connects two bots that will play against         ║
    ║  each other in various mini-games.                ║
    ║                                                   ║
    ║  Make sure the server is running on port 8080!    ║
    ╚═══════════════════════════════════════════════════╝
    """)
    asyncio.run(main())
