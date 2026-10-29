# shop

An online shop's order service. A customer places an order, the service reserves the items in stock and emails a confirmation. An order can be cancelled: the items go back to stock and the customer gets an email. When an item runs low, the warehouse is notified.

Stack: FastAPI, SQLAlchemy, SQLite, Celery + Redis for background jobs.

| Module | What it does |
|---|---|
| `app/orders` | placing and cancelling orders |
| `app/inventory` | stock levels and reservations |
| `app/notifications` | emails to customers and the warehouse (Celery tasks) |
| `app/infra` | fake external systems: SMTP and an HTTP client. Like real ones, they are slow and sometimes fail. |

## Setup

Please do this before the interview: both commands must work.

```bash
make install && make test   # tests run Celery tasks in-process, no Redis needed
make up                     # api on http://localhost:8000/docs, worker, redis
```

The api and the worker reload on code changes. In docker compose the fake SMTP fails 20% of the time (`FAKE_SMTP_FAIL_RATE`). All commands: `make help`.

## Task

The code in front of you is not great. Find its weak spots and rewrite it the way you would want to see it.

What we know from management: **the `orders`, `inventory` and `notifications` modules will soon be owned by different teams.** Each team wants to change its own module (models, tables, internal logic) without breaking other teams' code and without coordinating every change with them. Deploy and the database stay shared for now. Prepare the codebase for this.

Business rule: if an item is out of stock, the order is not created. The customer gets a 409 and nothing is reserved.

## Ground rules

- Use any AI tools you normally use. Share your screen and think out loud: how you steer the tool matters to us as much as the final code.
- Commit in small steps. We read the history.
- Keep stable what other systems depend on:
  - the HTTP API: paths, request and response shapes, status codes;
  - the DB schema: existing tables and columns stay, new ones are fine;
  - `app.main:app` and the `DATABASE_URL` env var;
  - the behaviour of `app/infra/`.
- You have about 50 minutes. You will not finish everything, and that is fine: tell us what you would do next.
