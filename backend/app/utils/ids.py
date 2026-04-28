import time
import random
import string


def new_id() -> str:
    timestamp = int(time.time() * 1000)
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{timestamp:013x}{suffix}"
