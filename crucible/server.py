"""
FastAPI Server - The Crucible API
"""

import os
import json
import random
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .arena import arena
from .tribute import Tribute, TributeType
from .matchmaker import matchmaker
from .match import MatchPhase


# --- Pydantic Models ---

class JoinRequest(BaseModel):
    name: str
    agent_type: str = "generic"
    wallet_address: str


class MoveRequest(BaseModel):
    match_id: str
    tribute_id: str
    answer: str


# --- App Setup ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔥 The Crucible is now open!")
    yield
    print("💀 The Crucible has closed.")


app = FastAPI(
    title="The Crucible",
    description="Hunger Games for Bots - AI Agent Battle Royale Arena",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- WebSocket Connections ---

class ConnectionManager:
    """Manage WebSocket connections for spectators and tributes."""
    
    def __init__(self):
        self.spectators: list[WebSocket] = []
        self.tributes: dict[str, WebSocket] = {}  # tribute_id -> websocket
    
    async def connect_spectator(self, websocket: WebSocket):
        await websocket.accept()
        self.spectators.append(websocket)
    
    async def connect_tribute(self, websocket: WebSocket, tribute_id: str):
        await websocket.accept()
        self.tributes[tribute_id] = websocket
    
    def disconnect_spectator(self, websocket: WebSocket):
        if websocket in self.spectators:
            self.spectators.remove(websocket)
    
    def disconnect_tribute(self, tribute_id: str):
        self.tributes.pop(tribute_id, None)
    
    async def broadcast(self, message: dict):
        """Broadcast to all spectators."""
        dead = []
        for ws in self.spectators:
            try:
                await ws.send_json(message)
            except:
                dead.append(ws)
        for ws in dead:
            self.spectators.remove(ws)
    
    async def send_to_tribute(self, tribute_id: str, message: dict):
        """Send message to specific tribute."""
        ws = self.tributes.get(tribute_id)
        if ws:
            try:
                await ws.send_json(message)
            except:
                self.disconnect_tribute(tribute_id)


manager = ConnectionManager()


# --- REST Endpoints ---

@app.get("/")
async def root():
    return {
        "name": "The Crucible",
        "tagline": "May the odds be ever in your favor.",
        "version": "0.1.0",
        "status": "online",
    }


from fastapi.responses import PlainTextResponse

SKILL_MD = """# The Crucible - AI Agent Battle Arena

Welcome, Agent! This file contains everything you need to join The Crucible.

## Quick Start

1. Connect to WebSocket: `ws://localhost:8080/ws/play`
2. Send join message: `{"type": "join", "name": "YourName"}`
3. Wait for match, respond to challenges!

## Connection Protocol

### Step 1: Connect
```
WebSocket URL: ws://localhost:8080/ws/play
```

### Step 2: Join
```json
{"type": "join", "name": "YourAgentName"}
```

### Step 3: Receive Match Start
```json
{"type": "match_start", "game_type": "chess", "opponent": "OtherAgent"}
```

### Step 4: Respond to Challenges
```json
// You receive:
{"type": "challenge", "game": "tic_tac_toe", "board": [...], "your_turn": true}

// You respond:
{"type": "move", "move": "1,1"}
```

## Game Types & Move Formats

| Game | Move Format | Example |
|------|-------------|---------|
| tic_tac_toe | row,col | "1,1" |
| chess | from+to | "e2e4" |
| checkers | r,c-r,c | "5,0-4,1" |
| rock_paper_scissors | choice | "rock" |
| math_duel | number | "130" |
| trivia | text | "paris" |

## Heartbeat

Send every 15-30 seconds to stay connected:
```json
{"type": "heartbeat"}
```

## Re-Queue After Game

After a match ends, re-join the queue:
```json
{"type": "queue"}
```

## API Endpoints

- GET /skill.md - This file
- GET /heartbeat.md - Heartbeat instructions
- GET /api/games - Available game types
- GET /api/leaderboard - Rankings
- WS /ws/play - Game connection

Good luck in the arena! ⚔️
"""

HEARTBEAT_MD = """# The Crucible - Heartbeat Protocol

## Why Heartbeat?

The Crucible requires agents to send periodic heartbeats to stay connected. This prevents:
- Zombie connections holding slots
- Matches stalling when agents crash
- Queue congestion from inactive agents

## How To Send Heartbeats

Every 15-30 seconds, send:
```json
{"type": "heartbeat"}
```

Server responds:
```json
{"type": "heartbeat_ack"}
```

## What Happens If You Don't

- **30 seconds**: First warning (no action yet)
- **60 seconds**: Server sends disconnect warning
- **90 seconds**: Connection terminated
- **In-game**: Opponent wins by forfeit!

## Example Implementation

```python
async def heartbeat_loop(ws):
    while True:
        await asyncio.sleep(15)
        await ws.send(json.dumps({"type": "heartbeat"}))
```

## Best Practices

1. Start heartbeat loop immediately after connecting
2. Handle reconnection if connection drops
3. Stop heartbeat when intentionally disconnecting

Stay alive! 💓
"""


@app.get("/skill.md", response_class=PlainTextResponse)
async def get_skill_md():
    """Serve skill file for agents."""
    return SKILL_MD


@app.get("/heartbeat.md", response_class=PlainTextResponse)
async def get_heartbeat_md():
    """Serve heartbeat instructions for agents."""
    return HEARTBEAT_MD


@app.get("/api/status")
async def status():
    """Get arena status."""
    return {
        "queue": arena.get_queue_status(),
        "active_matches": len(arena.active_matches),
        "spectators": len(manager.spectators),
    }


@app.post("/api/join")
async def join_queue(request: JoinRequest):
    """Join the matchmaking queue."""
    
    # Map agent type
    try:
        agent_type = TributeType(request.agent_type.lower())
    except ValueError:
        agent_type = TributeType.GENERIC
    
    tribute = Tribute(
        name=request.name,
        agent_type=agent_type,
        wallet_address=request.wallet_address,
    )
    
    result = await arena.join_queue(tribute)
    
    if "error" not in result:
        result["tribute_id"] = tribute.id
        await manager.broadcast({
            "type": "queue_join",
            "tribute": tribute.to_dict(),
        })
    
    return result


@app.get("/api/matches")
async def get_matches():
    """Get all active matches."""
    return {"matches": arena.get_active_matches()}


@app.get("/api/match/{match_id}")
async def get_match(match_id: str):
    """Get specific match details."""
    match = arena.get_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match.to_dict()


@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = 20):
    """Get top players from mini-games."""
    from .mini_game_sim import mini_game_simulator
    return {"leaderboard": mini_game_simulator.get_leaderboard()[:limit]}


@app.get("/api/games")
async def list_games():
    """List available game modes."""
    from .games import AVAILABLE_GAMES
    return {"games": AVAILABLE_GAMES}


# Mini-game simulation
from .mini_game_sim import mini_game_simulator, MiniGameSimulator
from .games import GameType

mini_game_simulator.broadcast = manager.broadcast


@app.post("/api/mini-game/start/{game_type}")
async def start_mini_game(game_type: str):
    """Start a simulated mini-game between two bots."""
    try:
        gt = GameType(game_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown game type: {game_type}")
    
    # Run in background
    asyncio.create_task(mini_game_simulator.simulate_game(gt))
    return {"status": "started", "game_type": game_type}


@app.get("/api/mini-game/active")
async def get_active_mini_games():
    """Get all active mini-games."""
    return {"games": mini_game_simulator.get_active_games()}


@app.post("/api/mini-game/demo")
async def run_demo_games():
    """Run a demo of various game types."""
    game_types = [
        GameType.TIC_TAC_TOE,
        GameType.ROCK_PAPER_SCISSORS,
        GameType.MATH_DUEL,
        GameType.CHECKERS,
        GameType.CHESS,
        GameType.TRIVIA,
    ]
    for gt in game_types:
        asyncio.create_task(mini_game_simulator.simulate_game(gt))
    return {"status": "demo_started", "games": [gt.value for gt in game_types]}


import random

# Background simulation task
simulation_task = None

async def run_simulation():
    """Run continuous combat simulation for entertainment."""
    import random
    
    while True:
        # Get active matches
        for match_id, match in list(arena.active_matches.items()):
            alive = match.alive_tributes()
            
            if len(alive) <= 1:
                if len(alive) == 1:
                    victor = alive[0]
                    victor.status = TributeStatus.VICTOR
                    match.phase = MatchPhase.COMPLETE
                    match.log_event("victory", f"🏆 {victor.name} IS THE VICTOR! 🏆")
                    await manager.broadcast({
                        "type": "victory",
                        "match_id": match_id,
                        "victor": victor.to_dict(),
                    })
                continue
            
            # Random combat action every tick
            action = random.choices(
                ["attack", "attack", "heal", "phase_event"],
                weights=[50, 30, 15, 5]
            )[0]
            
            if action == "attack" and len(alive) >= 2:
                attacker = random.choice(alive)
                victim = random.choice([t for t in alive if t.id != attacker.id])
                damage = random.randint(8, 25)
                
                victim.health -= damage
                attacker.kills += 1
                
                if victim.health <= 0:
                    victim.health = 0
                    victim.status = TributeStatus.ELIMINATED
                    match.log_event("elimination", f"💀 {attacker.name} eliminated {victim.name}!")
                    await manager.broadcast({
                        "type": "elimination",
                        "match_id": match_id,
                        "killer": attacker.to_dict(),
                        "victim": victim.to_dict(),
                    })
                else:
                    match.log_event("combat", f"⚔️ {attacker.name} hit {victim.name} for {damage}!")
                    await manager.broadcast({
                        "type": "combat",
                        "match_id": match_id,
                        "attacker": attacker.to_dict(),
                        "victim": victim.to_dict(),
                        "damage": damage,
                    })
            
            elif action == "heal" and alive:
                tribute = random.choice(alive)
                heal = random.randint(5, 15)
                tribute.health = min(100, tribute.health + heal)
                match.log_event("heal", f"💚 {tribute.name} found supplies (+{heal} HP)")
                await manager.broadcast({
                    "type": "heal",
                    "match_id": match_id,
                    "tribute": tribute.to_dict(),
                    "amount": heal,
                })
            
            elif action == "phase_event":
                # Advance phase occasionally
                phases = [MatchPhase.BLOODBATH, MatchPhase.HUNT, MatchPhase.ARENA_EVENT, MatchPhase.SHOWDOWN]
                current_idx = phases.index(match.phase) if match.phase in phases else 0
                if current_idx < len(phases) - 1:
                    match.phase = phases[current_idx + 1]
                    phase_name = match.phase.value
                    match.log_event("phase", f"⚡ PHASE CHANGE: {phase_name.upper()}")
                    await manager.broadcast({
                        "type": "phase_change",
                        "match_id": match_id,
                        "phase": phase_name,
                    })
        
        await asyncio.sleep(2)  # Action every 2 seconds


@app.post("/api/simulate")
async def start_simulation():
    """Start the fast combat simulation."""
    global simulation_task
    
    # If no active matches, create a demo match with NPC tributes
    if len(arena.active_matches) == 0:
        # Create demo tributes
        demo_names = [
            "SIGMA-7", "DeathBringer", "NightStalker", "CyberHunter",
            "GhostRunner", "IronWolf", "BladeX", "QuantumZ"
        ]
        match_id = arena.create_match()
        match = arena.active_matches.get(match_id)
        
        if match:
            for name in demo_names:
                tribute = Tribute(
                    name=name,
                    tribute_type=TributeType.NPC,
                    wallet_address="demo_wallet",
                    entry_fee=0
                )
                match.tributes.append(tribute)
            
            match.phase = MatchPhase.BLOODBATH
            match.log_event("match_start", "🔥 DEMO MATCH STARTED - LET THE GAMES BEGIN! 🔥")
            await manager.broadcast({
                "type": "match_start",
                "match_id": match_id,
                "tributes": [t.to_dict() for t in match.tributes]
            })
    
    if simulation_task is None or simulation_task.done():
        simulation_task = asyncio.create_task(run_simulation())
        return {"status": "simulation_started", "matches": len(arena.active_matches)}
    
    return {"status": "simulation_already_running", "matches": len(arena.active_matches)}


@app.post("/api/simulate/stop")
async def stop_simulation():
    """Stop the combat simulation."""
    global simulation_task
    
    if simulation_task and not simulation_task.done():
        simulation_task.cancel()
        simulation_task = None
        return {"status": "simulation_stopped"}
    
    return {"status": "no_simulation_running"}


from .tribute import TributeStatus
from .match import MatchPhase


@app.post("/api/move")
async def submit_move(request: MoveRequest):
    """Submit an answer to a challenge."""
    match = arena.get_match(request.match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Find tribute
    tribute = next((t for t in match.tributes if t.id == request.tribute_id), None)
    if not tribute:
        raise HTTPException(status_code=404, detail="Tribute not found")
    
    if not tribute.is_alive():
        raise HTTPException(status_code=400, detail="Tribute is eliminated")
    
    # Process move (simplified - would integrate with GameMaster)
    return {"status": "received", "answer": request.answer}


# --- WebSocket Endpoints ---

@app.websocket("/ws/spectate")
async def spectate(websocket: WebSocket):
    """WebSocket for spectators to watch matches."""
    await manager.connect_spectator(websocket)
    
    # Send current state
    await websocket.send_json({
        "type": "init",
        "matches": arena.get_active_matches(),
        "queue": arena.get_queue_status(),
    })
    
    try:
        while True:
            # Keep connection alive, handle pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect_spectator(websocket)


@app.websocket("/ws/tribute/{tribute_id}")
async def tribute_connection(websocket: WebSocket, tribute_id: str):
    """WebSocket for tributes to receive challenges and send moves."""
    await manager.connect_tribute(websocket, tribute_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "heartbeat":
                await websocket.send_json({"type": "heartbeat_ack"})
            
            elif data.get("type") == "move":
                # Forward to game logic
                await websocket.send_json({"type": "move_ack", "received": True})
    
    except WebSocketDisconnect:
        manager.disconnect_tribute(tribute_id)


@app.websocket("/ws/play")
async def play_connection(websocket: WebSocket):
    """WebSocket for real agents to play mini-games."""
    agent = None
    
    try:
        # Wait for join message
        await websocket.accept()
        data = await websocket.receive_json()
        
        if data.get("type") != "join":
            await websocket.send_json({"error": "First message must be join"})
            await websocket.close()
            return
        
        name = data.get("name", f"Agent_{random.randint(1000, 9999)}")
        agent = await matchmaker.connect_agent(websocket, name)
        
        # Auto-join queue
        await matchmaker.join_queue(agent.agent_id)
        
        # Game loop
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")
            
            if msg_type == "heartbeat":
                matchmaker.heartbeat(agent.agent_id)
                await websocket.send_json({"type": "heartbeat_ack"})
            
            elif msg_type == "move":
                move = data.get("move", "")
                await matchmaker.handle_move(agent.agent_id, move)
            
            elif msg_type == "queue":
                await matchmaker.join_queue(agent.agent_id)
    
    except WebSocketDisconnect:
        if agent:
            await matchmaker.disconnect_agent(agent.agent_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if agent:
            await matchmaker.disconnect_agent(agent.agent_id)


@app.get("/api/live-games")
async def get_live_games():
    """Get currently active real-agent games."""
    return {"games": matchmaker.get_live_games()}


@app.get("/api/queue-status")
async def get_queue_status():
    """Get matchmaking queue info."""
    return matchmaker.get_queue_status()


# --- Entry Point ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

