from typing import TypedDict, Tuple


class State(TypedDict):
    log: dict | None
    tools: list | None
    AnomalyDetector: Tuple[bool, str]  # (is_anomaly, explanation)