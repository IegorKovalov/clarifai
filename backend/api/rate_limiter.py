from collections import defaultdict, deque
import time


class SlidingWindowRateLimiter:
    """
    Per-key sliding window rate limiter backed by in-memory deques.
    Each key gets its own timestamp queue. Requests outside the window
    are evicted on every check — no background cleanup needed.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: defaultdict[str, deque] = defaultdict(deque)

    def check(self, key: str) -> tuple[bool, int]:
        """
        Returns (is_allowed, retry_after_seconds).
        Calling this also records the request if allowed.
        """
        now = time.time()
        window_start = now - self.window_seconds

        dq = self._timestamps[key]
        while dq and dq[0] < window_start:
            dq.popleft()

        if len(dq) >= self.max_requests:
            retry_after = int(dq[0] - window_start) + 1
            return False, retry_after

        dq.append(now)
        return True, 0


# Shared instance — 60 chat requests per tenant per minute
chat_rate_limiter = SlidingWindowRateLimiter(max_requests=60, window_seconds=60)
