"""Fake SMTP. Simulates an external mail provider: slow and sometimes down.

Do not change the behaviour of this file: it stands in for a real network service.
"""
import os
import random
import time

_rng = random.SystemRandom()  # no shared state between forked Celery workers
from dataclasses import dataclass, field


class EmailError(Exception):
    pass


@dataclass
class FakeMailer:
    latency: float = float(os.environ.get("FAKE_SMTP_LATENCY", "0.05"))
    fail_rate: float = float(os.environ.get("FAKE_SMTP_FAIL_RATE", "0"))
    fail_next: int = 0  # tests set this to make the next N sends fail
    sent: list[dict] = field(default_factory=list)
    on_send: list = field(default_factory=list)  # hooks called before each send

    def send(self, to: str, subject: str, body: str) -> None:
        for hook in self.on_send:
            hook(to, subject, body)
        time.sleep(self.latency)
        if self.fail_next > 0:
            self.fail_next -= 1
            raise EmailError(f"SMTP timeout while sending to {to}")
        if _rng.random() < self.fail_rate:
            raise EmailError(f"SMTP timeout while sending to {to}")
        self.sent.append({"to": to, "subject": subject, "body": body})

    def reset(self) -> None:
        self.fail_next = 0
        self.sent.clear()
        self.on_send.clear()


mailer = FakeMailer()


def send_email(to: str, subject: str, body: str) -> None:
    mailer.send(to, subject, body)
