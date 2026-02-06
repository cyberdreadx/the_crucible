"""
Arena - Main orchestrator for matches and spectators.
"""

import asyncio
from typing import Optional
from datetime import datetime

from .tribute import Tribute, TributeType
from .match import Match, MatchPhase
from .game_master import GameMaster


class Arena:
    """
    The Arena manages active matches, matchmaking queue, and spectators.
    """
    
    def __init__(self):
        self.active_matches: dict[str, Match] = {}
        self.game_masters: dict[str, GameMaster] = {}
        self.queue: list[Tribute] = []
        self.leaderboard: dict[str, dict] = {}  # wallet_address -> stats
        
        # Settings
        self.min_tributes = 4
        self.max_tributes = 16
        self.entry_fee = 100
    
    async def join_queue(self, tribute: Tribute) -> dict:
        """Add a tribute to the matchmaking queue."""
        
        # Check if already in queue
        if any(t.id == tribute.id for t in self.queue):
            return {"error": "Already in queue"}
        
        self.queue.append(tribute)
        
        # Check if we can start a match
        if len(self.queue) >= self.min_tributes:
            match = await self.create_match()
            return {"status": "match_starting", "match_id": match.id}
        
        return {
            "status": "queued",
            "position": len(self.queue),
            "waiting_for": self.min_tributes - len(self.queue),
        }
    
    async def create_match(self) -> Match:
        """Create a new match from queued tributes."""
        
        # Take up to max_tributes from queue
        tributes = self.queue[:self.max_tributes]
        self.queue = self.queue[self.max_tributes:]
        
        match = Match(
            entry_fee=self.entry_fee,
            min_tributes=self.min_tributes,
            max_tributes=self.max_tributes,
        )
        
        for tribute in tributes:
            match.add_tribute(tribute)
        
        self.active_matches[match.id] = match
        
        # Create game master
        gm = GameMaster(match)
        self.game_masters[match.id] = gm
        
        # Start match in background
        asyncio.create_task(self._run_match(match.id))
        
        return match
    
    async def _run_match(self, match_id: str):
        """Run a match to completion."""
        gm = self.game_masters.get(match_id)
        if not gm:
            return
        
        try:
            await gm.run_match()
        finally:
            # Update leaderboard
            match = self.active_matches.get(match_id)
            if match:
                await self._update_leaderboard(match)
            
            # Cleanup after some time
            await asyncio.sleep(300)  # Keep match data for 5 minutes
            self.active_matches.pop(match_id, None)
            self.game_masters.pop(match_id, None)
    
    async def _update_leaderboard(self, match: Match):
        """Update leaderboard after match completion."""
        for tribute in match.tributes:
            if tribute.wallet_address not in self.leaderboard:
                self.leaderboard[tribute.wallet_address] = {
                    "name": tribute.name,
                    "wins": 0,
                    "losses": 0,
                    "kills": 0,
                    "elo": 1000,
                    "earnings": 0,
                }
            
            stats = self.leaderboard[tribute.wallet_address]
            stats["kills"] += tribute.kills
            
            if tribute.status.value == "victor":
                stats["wins"] += 1
                stats["earnings"] += match.prize_pool
                stats["elo"] += 25
            else:
                stats["losses"] += 1
                stats["elo"] = max(0, stats["elo"] - 15)
    
    def get_match(self, match_id: str) -> Optional[Match]:
        """Get a match by ID."""
        return self.active_matches.get(match_id)
    
    def get_active_matches(self) -> list[dict]:
        """Get all active matches."""
        return [m.to_dict() for m in self.active_matches.values()]
    
    def get_leaderboard(self, limit: int = 20) -> list[dict]:
        """Get top players by ELO."""
        sorted_players = sorted(
            self.leaderboard.items(),
            key=lambda x: x[1]["elo"],
            reverse=True,
        )
        return [
            {"wallet": addr, **stats}
            for addr, stats in sorted_players[:limit]
        ]
    
    def get_queue_status(self) -> dict:
        """Get current queue status."""
        return {
            "queue_size": len(self.queue),
            "waiting_for": max(0, self.min_tributes - len(self.queue)),
            "active_matches": len(self.active_matches),
        }


# Global arena instance
arena = Arena()
