"""
Tribute - Represents an AI agent participant in The Crucible.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime
import uuid


class TributeStatus(Enum):
    """Status of a tribute in the arena."""
    WAITING = "waiting"      # In queue, not yet in match
    ALIVE = "alive"          # Active in match
    ELIMINATED = "eliminated" # Dead
    VICTOR = "victor"        # Winner


class TributeType(Enum):
    """Type of AI agent."""
    GLTCH = "gltch"
    OPENCLAW = "openclaw"
    GENERIC = "generic"


@dataclass
class Tribute:
    """An AI agent participating in The Crucible."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    agent_type: TributeType = TributeType.GENERIC
    wallet_address: str = ""
    
    # Match state
    status: TributeStatus = TributeStatus.WAITING
    health: int = 100
    resources: int = 0
    kills: int = 0
    
    # Rating
    elo: int = 1000
    wins: int = 0
    losses: int = 0
    
    # Connection
    websocket: Optional[object] = field(default=None, repr=False)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    
    def is_alive(self) -> bool:
        return self.status == TributeStatus.ALIVE
    
    def eliminate(self, killed_by: Optional["Tribute"] = None):
        """Mark tribute as eliminated."""
        self.status = TributeStatus.ELIMINATED
        self.health = 0
        if killed_by:
            killed_by.kills += 1
    
    def take_damage(self, amount: int) -> bool:
        """Apply damage. Returns True if eliminated."""
        self.health = max(0, self.health - amount)
        if self.health == 0:
            self.status = TributeStatus.ELIMINATED
            return True
        return False
    
    def crown_victor(self):
        """Mark as the winner."""
        self.status = TributeStatus.VICTOR
        self.wins += 1
    
    def to_dict(self) -> dict:
        """Serialize for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.agent_type.value,
            "status": self.status.value,
            "health": self.health,
            "resources": self.resources,
            "kills": self.kills,
            "elo": self.elo,
        }
