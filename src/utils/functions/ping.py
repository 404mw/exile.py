def get_ping_response(latency: float) -> str:
    """
    Returns a simple ping response with latency in milliseconds.
    """
    ms = round(latency * 1000)
    return f"Pong! 🏓 Latency: {ms}ms"
