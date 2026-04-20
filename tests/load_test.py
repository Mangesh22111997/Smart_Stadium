import time
import httpx
import asyncio
from datetime import datetime

# Configuration
BASE_URL = "https://stadium-backend-771554077981.asia-south1.run.app"
CONCURRENT_USERS = 50
TOTAL_REQUESTS = 500

async def simulate_user_flow(client: httpx.AsyncClient, user_id: int):
    """
    Simulate a typical stadium user journey:
    1. Check health
    2. List events
    3. Get gate status
    """
    start_time = time.time()
    try:
        # 1. Health check
        await client.get("/health")
        
        # 2. List events
        await client.get("/events/list")
        
        # 3. Check gate A status
        await client.get("/gates/A")
        
        duration = time.time() - start_time
        return True, duration
    except Exception as e:
        print(f"User {user_id} failed: {e}")
        return False, 0

async def run_load_test():
    print(f"🚀 Starting Load Test: {CONCURRENT_USERS} concurrent users, {TOTAL_REQUESTS} total requests")
    print(f"Target: {BASE_URL}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = []
        for i in range(TOTAL_REQUESTS):
            tasks.append(simulate_user_flow(client, i))
            
            # Simple throttling to maintain concurrency
            if len(tasks) >= CONCURRENT_USERS:
                results = await asyncio.gather(*tasks)
                tasks = []
        
        if tasks:
            results = await asyncio.gather(*tasks)

    # Calculate metrics
    successes = [r for r in results if r[0]]
    durations = [r[1] for r in results if r[0]]
    
    avg_lat = sum(durations) / len(durations) if durations else 0
    
    print("\n--- Load Test Results ---")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Success Rate:   {(len(successes)/TOTAL_REQUESTS)*100:.2f}%")
    print(f"Avg Latency:    {avg_lat*1000:.2f}ms")
    print(f"Test Finished:  {datetime.now().isoformat()}")

if __name__ == "__main__":
    asyncio.run(run_load_test())
