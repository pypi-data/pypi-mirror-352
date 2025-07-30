class CustomIndicator:
    data = dict(
        bar_index=0,
        last_bar_index=0,
        close=0,
        open=0,

    )

    def __init__(self):
        bar_index: int = 0
        last_bar_index: int = 0
        close: float = 0
        open_val: float = 0
        high: float = 0
        low: float = 0
