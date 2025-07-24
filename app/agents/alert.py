def alert(state):
    log = state.get("log")
    anomaly_result = state.get("AnomalyDetector", (False, ""))

    if not log:
        print("[AlertAgent] No log found in state.")
        return {}

    _, explanation = anomaly_result

    alert_payload = {
        "source": log.get("source"),
        "level": log.get("level"),
        "message": log.get("message"),
        "timestamp": log.get("timestamp"),
        "explanation": explanation
    }

    print("[AlertAgent] ALERT TRIGGERED:", alert_payload)

    return {}