import asyncio
import json
import httpx

async def test():
    async with httpx.AsyncClient() as client:
        # Assuming backend is on port 8000
        req = {
            "text": "The general problem of simulating (or creating) intelligence has been broken into subproblems.",
            "threshold": 0.75,
            "max_sentences": 2
        }
        resp = await client.post("http://127.0.0.1:8000/api/check", json=req, timeout=30.0)
        print("Status", resp.status_code)
        print("Response", json.dumps(resp.json(), indent=2))

asyncio.run(test())
