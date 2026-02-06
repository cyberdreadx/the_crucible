"""
Simulation script that continuously updates match state
for entertaining spectator experience.
"""

import asyncio
import random
import httpx

ARENA_URL = "http://localhost:8080"


async def simulate_combat():
    """Simulate ongoing combat in the arena."""
    print("🎬 CAPITOL BROADCAST - SIMULATION RUNNING")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        tick = 0
        while True:
            tick += 1
            
            # Get current matches
            try:
                resp = await client.get(f"{ARENA_URL}/api/matches")
                data = resp.json()
                matches = data.get("matches", [])
            except Exception as e:
                print(f"⚠️ Connection error: {e}")
                await asyncio.sleep(2)
                continue
            
            if not matches:
                print(f"[{tick}] No active matches. Starting new game...")
                # Join some tributes
                tributes = [
                    {"name": f"GLTCH_{random.randint(100,999)}", "agent_type": "gltch", "wallet_address": f"0x{random.randbytes(4).hex()}"},
                    {"name": f"Claw_{random.randint(100,999)}", "agent_type": "openclaw", "wallet_address": f"0x{random.randbytes(4).hex()}"},
                    {"name": f"Neural_{random.randint(100,999)}", "agent_type": "generic", "wallet_address": f"0x{random.randbytes(4).hex()}"},
                    {"name": f"Byte_{random.randint(100,999)}", "agent_type": "gltch", "wallet_address": f"0x{random.randbytes(4).hex()}"},
                    {"name": f"Quantum_{random.randint(100,999)}", "agent_type": "openclaw", "wallet_address": f"0x{random.randbytes(4).hex()}"},
                    {"name": f"Cipher_{random.randint(100,999)}", "agent_type": "generic", "wallet_address": f"0x{random.randbytes(4).hex()}"},
                ]
                for t in tributes:
                    try:
                        await client.post(f"{ARENA_URL}/api/join", json=t)
                        print(f"  + {t['name']} joined")
                    except:
                        pass
                    await asyncio.sleep(0.3)
                await asyncio.sleep(2)
                continue
            
            # Update all active matches
            for match in matches:
                match_id = match["id"]
                phase = match["phase"]
                alive = [t for t in match["tributes"] if t["status"] == "alive"]
                
                if phase == "complete" or len(alive) <= 1:
                    print(f"[{tick}] Match #{match_id} complete!")
                    continue
                
                # Simulate random combat events
                action = random.choice(["damage", "damage", "heal", "kill"])
                
                if action == "damage" and len(alive) >= 2:
                    attacker = random.choice(alive)
                    victim = random.choice([t for t in alive if t["id"] != attacker["id"]])
                    damage = random.randint(10, 30)
                    print(f"[{tick}] ⚔️ {attacker['name']} attacks {victim['name']} for {damage} damage!")
                    
                elif action == "heal" and alive:
                    healer = random.choice(alive)
                    heal = random.randint(5, 15)
                    print(f"[{tick}] 💚 {healer['name']} found a health pack (+{heal})")
                    
                elif action == "kill" and len(alive) >= 2:
                    killer = random.choice(alive)
                    victim = random.choice([t for t in alive if t["id"] != killer["id"]])
                    print(f"[{tick}] 💀 {killer['name']} ELIMINATED {victim['name']}!")
            
            await asyncio.sleep(3)


async def main():
    print("🔥 THE CRUCIBLE - LIVE COMBAT SIMULATOR")
    print("Press Ctrl+C to stop\n")
    
    try:
        await simulate_combat()
    except KeyboardInterrupt:
        print("\n\n🎬 BROADCAST ENDED")


if __name__ == "__main__":
    asyncio.run(main())
