import redis
import time
import random

import os
redis_host = os.environ.get("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)

sources = ["web", "db", "auth", "api"]
levels = ["info", "warning", "error"]
messages = [
    "User logged in",
    "Database connection failed",
    "Unauthorized access attempt",
    "Request timeout",
    "Health check passed",
    "Disk usage exceeded threshold"
]

def generate_log():
    return {
        "source": random.choice(sources),
        "level": random.choice(levels),
        "message": random.choice(messages),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

for _ in range(10):
    log = generate_log()
    r.xadd("logs:incoming", log)
    print("[LogPusher] Inserted:", log)
    time.sleep(1)  # Optional: simulate live logs
