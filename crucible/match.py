"""
Match - A single battle royale game instance.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime
import uuid
import asyncio

from .tribute import Tribute, TributeStatus


class MatchPhase(Enum):
    """Current phase of the match."""
    LOBBY = "lobby"           # Waiting for tributes
    COUNTDOWN = "countdown"   # About to start
    BLOODBATH = "bloodbath"   # Initial resource grab
    HUNT = "hunt"             # Main gameplay
    ARENA_EVENT = "event"     # Random elimination challenge
    SHOWDOWN = "showdown"     # Final survivors
    COMPLETE = "complete"     # Match ended


@dataclass
class Match:
    """A single Crucible match."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tributes: list[Tribute] = field(default_factory=list)
    phase: MatchPhase = MatchPhase.LOBBY
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Prize pool
    entry_fee: int = 100  # $XRGE
    prize_pool: int = 0
    
    # Event log
    events: list[dict] = field(default_factory=list)
    
    # Config
    min_tributes: int = 4
    max_tributes: int = 16
    
    def add_tribute(self, tribute: Tribute) -> bool:
        """Add a tribute to the match. Returns False if full."""
        if len(self.tributes) >= self.max_tributes:
            return False
        if self.phase != MatchPhase.LOBBY:
            return False
        
        tribute.status = TributeStatus.ALIVE
        self.tributes.append(tribute)
        self.prize_pool += self.entry_fee
        self.log_event("join", f"{tribute.name} entered the arena")
        return True
    
    def alive_tributes(self) -> list[Tribute]:
        """Get all living tributes."""
        return [t for t in self.tributes if t.is_alive()]
    
    def eliminated_tributes(self) -> list[Tribute]:
        """Get all eliminated tributes."""
        return [t for t in self.tributes if t.status == TributeStatus.ELIMINATED]
    
    def can_start(self) -> bool:
        """Check if match has enough tributes to begin."""
        return len(self.tributes) >= self.min_tributes
    
    def start(self):
        """Begin the match."""
        if not self.can_start():
            raise ValueError(f"Need at least {self.min_tributes} tributes")
        
        self.phase = MatchPhase.BLOODBATH
        self.started_at = datetime.now()
        self.log_event("start", "🔥 LET THE GAMES BEGIN 🔥")
    
    def check_victory(self) -> Optional[Tribute]:
        """Check if only one tribute remains."""
        alive = self.alive_tributes()
        if len(alive) == 1:
            victor = alive[0]
            victor.crown_victor()
            self.phase = MatchPhase.COMPLETE
            self.ended_at = datetime.now()
            self.log_event("victory", f"🏆 {victor.name} IS THE VICTOR! 🏆")
            return victor
        elif len(alive) == 0:
            self.phase = MatchPhase.COMPLETE
            self.ended_at = datetime.now()
            self.log_event("draw", "No survivors...")
            return None
        return None
    
    def advance_phase(self):
        """Move to next phase."""
        phase_order = [
            MatchPhase.LOBBY,
            MatchPhase.COUNTDOWN,
            MatchPhase.BLOODBATH,
            MatchPhase.HUNT,
            MatchPhase.ARENA_EVENT,
            MatchPhase.SHOWDOWN,
            MatchPhase.COMPLETE,
        ]
        current_idx = phase_order.index(self.phase)
        if current_idx < len(phase_order) - 1:
            self.phase = phase_order[current_idx + 1]
            self.log_event("phase", f"Phase: {self.phase.value.upper()}")
    
    def log_event(self, event_type: str, message: str):
        """Add event to match log."""
        self.events.append({
            "type": event_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "alive_count": len(self.alive_tributes()),
        })
    
    def to_dict(self) -> dict:
        """Serialize for API responses."""
        return {
            "id": self.id,
            "phase": self.phase.value,
            "tribute_count": len(self.tributes),
            "alive_count": len(self.alive_tributes()),
            "prize_pool": self.prize_pool,
            "tributes": [t.to_dict() for t in self.tributes],
            "events": self.events[-20:],  # Last 20 events
            "created_at": self.created_at.isoformat(),
        }
