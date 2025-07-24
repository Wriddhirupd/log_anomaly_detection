

def normalize_log(state):
    log = state.get("log")
    if not log:
        return {"log": None}

    normalized = {
        "source": log.get("source", "unknown"),
        "message": log.get("message", "").lower(),
        "timestamp": log.get("timestamp", ""),
        "level": log.get("level", "info")
    }
    print("[Preprocessor] Normalized log:", normalized)
    return {"log": normalized}