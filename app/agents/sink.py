def sink_log(state):
    log = state.get("log")
    print("[LogSink] Log archived:", log)
    return {}