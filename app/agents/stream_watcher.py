import redis
import json
import os
redis_host = os.environ.get("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)

# Fetch a single log entry from the Redis stream
# Returns the raw log dictionary or None if empty

def fetch_log_from_stream(state):
    print("[StreamWatcher] Fetching log from Redis stream...")
    log = state.get("log")
    print(f"log in fetch_log_from_stream: {log}")
    # if not log or not isinstance(log, dict):
    #     return {"log": None}
    result = r.xread({"logs:incoming": "$"}, block=1000, count=1)
    if result:
        _, entries = result[0]
        stream_id, data = entries[0]
        log = {k: v for k, v in data.items()}
        print("[StreamWatcher] New log:", log)
        return {"log": log}
    return {"log": None}
