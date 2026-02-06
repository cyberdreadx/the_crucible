"""
Game Master - Controls match flow and arena events.
"""

import asyncio
import random
from datetime import datetime
from typing import Optional, Callable

from .match import Match, MatchPhase
from .tribute import Tribute, TributeStatus
from .challenges import Challenge, get_random_challenge, ChallengeResult


class GameMaster:
    """
    The Game Master controls the flow of a Crucible match.
    Think of it as the AI overlord running the Hunger Games.
    """
    
    def __init__(self, match: Match):
        self.match = match
        self.current_challenge: Optional[Challenge] = None
        self.broadcast_callback: Optional[Callable] = None
        
        # Phase timings (seconds)
        self.bloodbath_duration = 60
        self.hunt_phase_duration = 300
        self.event_interval = 90
        self.move_timeout = 30
    
    async def broadcast(self, event_type: str, data: dict):
        """Broadcast event to all spectators and tributes."""
        if self.broadcast_callback:
            await self.broadcast_callback({
                "type": event_type,
                "match_id": self.match.id,
                "timestamp": datetime.now().isoformat(),
                **data,
            })
    
    async def run_match(self):
        """Execute the full match lifecycle."""
        
        # Countdown
        self.match.phase = MatchPhase.COUNTDOWN
        await self.broadcast("phase", {"phase": "countdown", "message": "Match starting in 10 seconds..."})
        await asyncio.sleep(10)
        
        # Start the games
        self.match.start()
        await self.broadcast("phase", {"phase": "bloodbath", "message": "🔥 LET THE GAMES BEGIN! 🔥"})
        
        # BLOODBATH - initial resource scramble
        await self.run_bloodbath()
        
        # Check for early victory
        if self.check_victory():
            return
        
        # HUNT PHASE - main gameplay
        await self.run_hunt_phase()
        
        # Check victory
        if self.check_victory():
            return
        
        # ARENA EVENT - elimination round
        await self.run_arena_event()
        
        # Check victory
        if self.check_victory():
            return
        
        # SHOWDOWN - final survivors face off
        await self.run_showdown()
    
    async def run_bloodbath(self):
        """
        Bloodbath Phase: All tributes race to complete a challenge.
        Slowest/failing tributes take damage.
        """
        self.match.phase = MatchPhase.BLOODBATH
        
        challenge = get_random_challenge(difficulty=3)
        prompt = challenge.generate()
        
        await self.broadcast("challenge", {
            "phase": "bloodbath",
            "challenge": prompt,
            "message": "🩸 BLOODBATH - First to solve survives unscathed!",
        })
        
        # In a real implementation, we'd wait for responses
        # For now, simulate some tributes failing
        await asyncio.sleep(self.bloodbath_duration)
        
        # Eliminate slowest 25%
        alive = self.match.alive_tributes()
        to_damage = random.sample(alive, k=max(1, len(alive) // 4))
        
        for tribute in to_damage:
            damage = random.randint(20, 40)
            eliminated = tribute.take_damage(damage)
            if eliminated:
                self.match.log_event("elimination", f"💀 {tribute.name} didn't survive the bloodbath")
                await self.broadcast("elimination", {"tribute": tribute.to_dict()})
            else:
                self.match.log_event("damage", f"{tribute.name} took {damage} damage")
    
    async def run_hunt_phase(self):
        """
        Hunt Phase: Tributes complete challenges and can attack each other.
        """
        self.match.phase = MatchPhase.HUNT
        await self.broadcast("phase", {"phase": "hunt", "message": "🎯 HUNT PHASE - Prove your worth or die trying"})
        
        rounds = 3
        for round_num in range(rounds):
            if len(self.match.alive_tributes()) <= 2:
                break
            
            challenge = get_random_challenge(difficulty=5)
            prompt = challenge.generate()
            
            await self.broadcast("challenge", {
                "round": round_num + 1,
                "challenge": prompt,
            })
            
            await asyncio.sleep(challenge.time_limit_seconds)
            
            # Simulate: random tribute fails and takes damage
            alive = self.match.alive_tributes()
            if alive:
                victim = random.choice(alive)
                damage = random.randint(15, 35)
                eliminated = victim.take_damage(damage)
                
                if eliminated:
                    self.match.log_event("elimination", f"💀 {victim.name} failed the challenge")
                    await self.broadcast("elimination", {"tribute": victim.to_dict()})
    
    async def run_arena_event(self):
        """
        Arena Event: A massive challenge that eliminates the weakest.
        """
        self.match.phase = MatchPhase.ARENA_EVENT
        
        events = [
            "☢️ RADIATION ZONE - Solve complex algorithms or take massive damage!",
            "🔥 FIREWALL - Break through the encryption or burn!",
            "⚡ LIGHTNING ROUND - 10 rapid-fire questions, miss 3 and you're dead!",
            "🌊 DATA FLOOD - Parse the incoming stream before you drown!",
        ]
        
        event = random.choice(events)
        await self.broadcast("arena_event", {"message": event})
        
        # Eliminate bottom 50% of remaining tributes
        alive = self.match.alive_tributes()
        to_eliminate = random.sample(alive, k=max(1, len(alive) // 2))
        
        for tribute in to_eliminate:
            tribute.eliminate()
            self.match.log_event("elimination", f"💀 {tribute.name} couldn't survive the arena event")
            await self.broadcast("elimination", {"tribute": tribute.to_dict()})
    
    async def run_showdown(self):
        """
        Showdown: Final survivors face off directly.
        """
        self.match.phase = MatchPhase.SHOWDOWN
        await self.broadcast("phase", {"phase": "showdown", "message": "⚔️ FINAL SHOWDOWN ⚔️"})
        
        while len(self.match.alive_tributes()) > 1:
            alive = self.match.alive_tributes()
            
            # Pick two tributes to duel
            if len(alive) >= 2:
                t1, t2 = random.sample(alive, k=2)
                
                challenge = get_random_challenge(difficulty=7)
                prompt = challenge.generate()
                
                await self.broadcast("duel", {
                    "tribute1": t1.to_dict(),
                    "tribute2": t2.to_dict(),
                    "challenge": prompt,
                    "message": f"⚔️ {t1.name} vs {t2.name}",
                })
                
                await asyncio.sleep(challenge.time_limit_seconds)
                
                # Random winner for now
                loser = random.choice([t1, t2])
                winner = t1 if loser == t2 else t2
                
                loser.eliminate(killed_by=winner)
                self.match.log_event("kill", f"💀 {winner.name} eliminated {loser.name}!")
                await self.broadcast("elimination", {
                    "tribute": loser.to_dict(),
                    "killed_by": winner.to_dict(),
                })
    
    def check_victory(self) -> bool:
        """Check if match has a victor."""
        victor = self.match.check_victory()
        if victor:
            asyncio.create_task(self.broadcast("victory", {
                "victor": victor.to_dict(),
                "prize_pool": self.match.prize_pool,
                "message": f"🏆 {victor.name} IS THE VICTOR! 🏆",
            }))
            return True
        return False
