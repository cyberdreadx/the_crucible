"""
Test script to simulate agents joining The Crucible.
Adds mock tributes to trigger a match.
"""

import asyncio
import httpx

ARENA_URL = "http://localhost:8080"

MOCK_TRIBUTES = [
    {"name": "GLTCH_Prime", "agent_type": "gltch", "wallet_address": "0xGLTCH001"},
    {"name": "ClawBot_Alpha", "agent_type": "openclaw", "wallet_address": "0xCLAW001"},
    {"name": "NeuralNinja", "agent_type": "generic", "wallet_address": "0xNEURAL01"},
    {"name": "ByteSlayer", "agent_type": "gltch", "wallet_address": "0xBYTE001"},
    {"name": "QuantumQuake", "agent_type": "openclaw", "wallet_address": "0xQUANT01"},
    {"name": "CipherStorm", "agent_type": "generic", "wallet_address": "0xCIPHER01"},
]


async def main():
    print("🔥 Simulating tributes joining The Crucible...\n")
    
    async with httpx.AsyncClient() as client:
        for tribute in MOCK_TRIBUTES:
            try:
                resp = await client.post(f"{ARENA_URL}/api/join", json=tribute)
                data = resp.json()
                print(f"  ✓ {tribute['name']} joined! Status: {data.get('status', 'unknown')}")
                
                if data.get("status") == "match_starting":
                    print(f"\n🎮 MATCH STARTING! ID: {data.get('match_id', '???')}")
                    
            except Exception as e:
                print(f"  ✗ {tribute['name']} failed: {e}")
            
            await asyncio.sleep(0.5)
    
    print("\n✅ Done! Check the UI at http://localhost:5174")


if __name__ == "__main__":
    asyncio.run(main())
