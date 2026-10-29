"""Fake outgoing HTTP client. Simulates calls to third-party services.

Do not change the behaviour of this file: it stands in for a real network service.
"""
import os
import time
from dataclasses import dataclass, field


class HttpError(Exception):
    pass


@dataclass
class FakeHttpClient:
    latency: float = float(os.environ.get("FAKE_HTTP_LATENCY", "0.05"))
    fail_next: int = 0
    calls: list[dict] = field(default_factory=list)
    on_call: list = field(default_factory=list)

    def post(self, url: str, json: dict) -> None:
        for hook in self.on_call:
            hook(url, json)
        time.sleep(self.latency)
        if self.fail_next > 0:
            self.fail_next -= 1
            raise HttpError(f"POST {url}: 503")
        self.calls.append({"url": url, "json": json})

    def reset(self) -> None:
        self.fail_next = 0
        self.calls.clear()
        self.on_call.clear()


http_client = FakeHttpClient()
