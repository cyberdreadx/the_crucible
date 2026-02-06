"""
Matchmaker - Handles real agent connections, queuing, and game matchmaking.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime
from fastapi import WebSocket
import random

from .games import GameType, create_game, Game, GameResult


@dataclass
class AgentConnection:
    """Represents a connected agent."""
    agent_id: str
    name: str
    websocket: WebSocket
    connected_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    in_game: bool = False
    current_game_id: Optional[str] = None


@dataclass
class LiveGame:
    """A game being played by real agents."""
    game_id: str
    game_type: GameType
    game: Game
    player1: AgentConnection
    player2: AgentConnection
    started_at: datetime = field(default_factory=datetime.now)
    moves: list = field(default_factory=list)
    finished: bool = False


class Matchmaker:
    """Manages agent connections, matchmaking queue, and live games."""
    
    def __init__(self, broadcast_callback=None):
        self.agents: dict[str, AgentConnection] = {}
        self.queue: list[str] = []  # agent_ids waiting for match
        self.live_games: dict[str, LiveGame] = {}
        self.game_counter = 0
        self.broadcast = broadcast_callback
        
        # Scores tracked separately
        self.scores: dict[str, dict] = {}
    
    async def connect_agent(self, websocket: WebSocket, name: str) -> AgentConnection:
        """Register a new agent connection."""
        await websocket.accept()
        
        agent_id = f"agent_{len(self.agents) + 1}_{random.randint(1000, 9999)}"
        agent = AgentConnection(
            agent_id=agent_id,
            name=name,
            websocket=websocket,
        )
        self.agents[agent_id] = agent
        
        # Send confirmation
        await websocket.send_json({
            "type": "connected",
            "agent_id": agent_id,
            "name": name,
        })
        
        print(f"🤖 Agent connected: {name} ({agent_id})")
        return agent
    
    async def disconnect_agent(self, agent_id: str):
        """Handle agent disconnect."""
        agent = self.agents.pop(agent_id, None)
        if agent:
            # Remove from queue
            if agent_id in self.queue:
                self.queue.remove(agent_id)
            
            # Handle in-game disconnect
            if agent.current_game_id:
                await self._forfeit_game(agent.current_game_id, agent_id)
            
            print(f"🔌 Agent disconnected: {agent.name}")
    
    async def join_queue(self, agent_id: str, game_type: Optional[str] = None):
        """Add agent to matchmaking queue."""
        agent = self.agents.get(agent_id)
        if not agent:
            return
        
        if agent_id not in self.queue and not agent.in_game:
            self.queue.append(agent_id)
            
            await agent.websocket.send_json({
                "type": "queued",
                "position": len(self.queue),
                "queue_size": len(self.queue),
            })
            
            if self.broadcast:
                await self.broadcast({
                    "type": "queue_update",
                    "queue_size": len(self.queue),
                })
            
            # Try to make a match
            await self._try_match()
    
    async def _try_match(self):
        """Try to create a match from queued agents."""
        if len(self.queue) < 2:
            return
        
        # Pop two agents
        agent1_id = self.queue.pop(0)
        agent2_id = self.queue.pop(0)
        
        agent1 = self.agents.get(agent1_id)
        agent2 = self.agents.get(agent2_id)
        
        if not agent1 or not agent2:
            return
        
        # Create game
        self.game_counter += 1
        game_id = f"live_game_{self.game_counter}"
        
        # Pick a random game type
        game_type = random.choice([
            GameType.TIC_TAC_TOE,
            GameType.ROCK_PAPER_SCISSORS,
            GameType.MATH_DUEL,
            GameType.TRIVIA,
            GameType.CHESS,
            GameType.CHECKERS,
        ])
        
        game = create_game(game_type, agent1_id, agent2_id)
        
        live_game = LiveGame(
            game_id=game_id,
            game_type=game_type,
            game=game,
            player1=agent1,
            player2=agent2,
        )
        
        self.live_games[game_id] = live_game
        
        # Mark agents as in-game
        agent1.in_game = True
        agent1.current_game_id = game_id
        agent2.in_game = True
        agent2.current_game_id = game_id
        
        # Notify players
        match_info = {
            "type": "match_start",
            "game_id": game_id,
            "game_type": game_type.value,
            "opponent": None,  # Will be set per-player
        }
        
        match_info["opponent"] = agent2.name
        await agent1.websocket.send_json(match_info)
        
        match_info["opponent"] = agent1.name
        await agent2.websocket.send_json(match_info)
        
        # Broadcast to spectators
        if self.broadcast:
            await self.broadcast({
                "type": "match_start",
                "game_id": game_id,
                "game_type": game_type.value,
                "player1": agent1.name,
                "player2": agent2.name,
            })
        
        # Send first challenge
        await self._send_challenges(live_game)
        
        print(f"⚔️ Match started: {agent1.name} vs {agent2.name} ({game_type.value})")
    
    async def _send_challenges(self, live_game: LiveGame):
        """Send current game state as challenge to players."""
        game = live_game.game
        
        # For turn-based games
        if hasattr(game, 'current_turn'):
            for player in [live_game.player1, live_game.player2]:
                prompt = game.get_prompt(player.agent_id)
                prompt["type"] = "challenge"
                await player.websocket.send_json(prompt)
        else:
            # Simultaneous games - send to both
            for player in [live_game.player1, live_game.player2]:
                prompt = game.get_prompt(player.agent_id)
                prompt["type"] = "challenge"
                await player.websocket.send_json(prompt)
    
    async def handle_move(self, agent_id: str, move: str):
        """Process a move from an agent."""
        agent = self.agents.get(agent_id)
        if not agent or not agent.current_game_id:
            return
        
        live_game = self.live_games.get(agent.current_game_id)
        if not live_game or live_game.finished:
            return
        
        game = live_game.game
        result = game.submit_move(agent_id, move)
        
        live_game.moves.append({
            "player": agent.name,
            "move": move,
        })
        
        # Broadcast move to spectators
        if self.broadcast:
            await self.broadcast({
                "type": "game_move",
                "game_id": live_game.game_id,
                "player": agent.name,
                "move": move,
                "state": game.get_state(),
            })
        
        if result:
            # Game over
            await self._end_game(live_game, result)
        else:
            # Send next challenge
            await self._send_challenges(live_game)
    
    async def _end_game(self, live_game: LiveGame, result: GameResult):
        """Handle game ending."""
        live_game.finished = True
        
        winner_id = result.winner_id
        winner = live_game.player1 if winner_id == live_game.player1.agent_id else live_game.player2
        loser = live_game.player2 if winner_id == live_game.player1.agent_id else live_game.player1
        
        # Update scores
        if winner.name not in self.scores:
            self.scores[winner.name] = {"wins": 0, "losses": 0, "games": 0}
        if loser.name not in self.scores:
            self.scores[loser.name] = {"wins": 0, "losses": 0, "games": 0}
        
        self.scores[winner.name]["wins"] += 1
        self.scores[winner.name]["games"] += 1
        self.scores[loser.name]["losses"] += 1
        self.scores[loser.name]["games"] += 1
        
        # Notify players
        end_msg = {
            "type": "match_end",
            "winner": winner.name,
            "message": result.message,
        }
        
        try:
            await live_game.player1.websocket.send_json(end_msg)
            await live_game.player2.websocket.send_json(end_msg)
        except:
            pass
        
        # Reset player state
        live_game.player1.in_game = False
        live_game.player1.current_game_id = None
        live_game.player2.in_game = False
        live_game.player2.current_game_id = None
        
        # Broadcast
        if self.broadcast:
            await self.broadcast({
                "type": "match_end",
                "game_id": live_game.game_id,
                "winner": winner.name,
                "message": result.message,
            })
        
        print(f"🏆 Match ended: {winner.name} wins!")
        
        # Cleanup after delay
        asyncio.create_task(self._cleanup_game(live_game.game_id, delay=10))
    
    async def _forfeit_game(self, game_id: str, forfeiter_id: str):
        """Handle forfeit when agent disconnects."""
        live_game = self.live_games.get(game_id)
        if not live_game:
            return
        
        winner = live_game.player1 if live_game.player2.agent_id == forfeiter_id else live_game.player2
        
        result = GameResult(
            winner_id=winner.agent_id,
            loser_id=forfeiter_id,
            message="🏃 Opponent disconnected - forfeit!",
        )
        
        await self._end_game(live_game, result)
    
    async def _cleanup_game(self, game_id: str, delay: int = 10):
        """Remove finished game after delay."""
        await asyncio.sleep(delay)
        self.live_games.pop(game_id, None)
    
    def heartbeat(self, agent_id: str):
        """Update agent's last heartbeat time."""
        agent = self.agents.get(agent_id)
        if agent:
            agent.last_heartbeat = datetime.now()
    
    def get_queue_status(self) -> dict:
        """Get current queue info."""
        return {
            "queue_size": len(self.queue),
            "active_games": len([g for g in self.live_games.values() if not g.finished]),
            "connected_agents": len(self.agents),
        }
    
    def get_live_games(self) -> list:
        """Get list of active games."""
        return [
            {
                "game_id": g.game_id,
                "game_type": g.game_type.value,
                "player1": g.player1.name,
                "player2": g.player2.name,
                "moves": len(g.moves),
                "finished": g.finished,
                "state": g.game.get_state(),
            }
            for g in self.live_games.values()
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


# Global matchmaker
matchmaker = Matchmaker()
