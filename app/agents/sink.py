def sink_log(state):
    log = state.get("log")
    print("[LogSink] ✅ Log archived:", log)
    # Optional: store into database, file, or another Redis stream
    return {}