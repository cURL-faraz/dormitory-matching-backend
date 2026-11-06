# Project Progress

> **Read this at the start of every session, before anything else.**
> **Update it** when a task is accepted, when the current task changes, when an issue is found or resolved, and at the end of any session that changed the project's state.
> Keep the past (history), what was checked (verified facts), and what was chosen (decisions) separate. Unknowns stay marked **Unresolved**. Never fill them with assumptions.

_Last updated: 2026-11-06_

---

## 1. Current checkpoint (verified 2026-11-06)

**Strategy (2026-11-06):** this repo is the **Phase 0 playground** for student auth. It follows the product owner's flows and stays structurally compatible with the team repo (`/Users/faraz/SD_405`). Verified work is transferred later (Phase 1) to the team branch `feat/students-otp`.

**Coding checkpoint:** the FastAPI app lives in the `app/` package with a `/health` router and typed settings (`app/core/config.py`). The app connects to PostgreSQL through an async engine (`app/db/session.py`) and exposes `GET /health/db` (200 / 503).

| Area | Verified state |
|---|---|
| Application code | `app/main.py` assembles the app; `app/api/routes/health.py` serves `GET /health` → `{"status": "healthy"}`. `app/core/config.py`: pydantic-settings `Settings` (`APP_ENV` Literal, required `DATABASE_URL`, `extra="ignore"`), cached via `lru_cache`. |
| Docker Compose | `compose.yaml` has one `db` service, **reviewed and accepted** on 2026-11-05: `postgres:17` (17.11 at the time), ports `"127.0.0.1:5432:5432"` (loopback only), `POSTGRES_DB: dormops_db`, `POSTGRES_USER: postgres` (development only, D-103), `POSTGRES_PASSWORD` from `.env` with `${…:?}` fail-fast, a `pg_isready` healthcheck over TCP (D-052), and the named volume `postgres_data`. No `container_name`. |
| Database runtime | Container `dormitory-matching-backend-db-1` was started and verified `(healthy)`. Startup takes about 3 s, most of which is the healthcheck interval. The volume `dormitory-matching-backend_postgres_data` holds the initialized cluster. Persistence across `down`/`up` was verified. |
| Database access | From the Mac: `psql -h 127.0.0.1 -p 5432 -U postgres -d dormops_db` works with the password (the connection arrives from `172.18.0.1`, so the `scram-sha-256` rule applies); a wrong password is rejected. Port 5432 is refused on the Wi-Fi IP. |
| DB client tools | `psql` 17.10 (Conda package `postgresql=17`, `defaults` channel) in the project Conda env. It is a development tool and is not visible to pip. |
| Secrets | `.env` (git-ignored) defines `POSTGRES_PASSWORD` and `DATABASE_URL` (`postgresql+asyncpg://…@127.0.0.1:5432/dormops_db`, password percent-encoded). `.env.example` is committed with `CHANGE_ME` placeholders. |
| Python env | Conda env `dormitory-matching-backend`, Python 3.14.8 |
| Git | Branch `main`. Latest commits: `0b4207f` (config), `dc36d83` (app package). `f822332` and earlier are pushed; `dc36d83` and `0b4207f` are **not pushed**. Remote `origin` → `github.com/cURL-faraz/dormitory-matching-backend` |
| Docs | CLAUDE.md restructured into CLAUDE.md, `docs/` and this file (2026-11-04). The original is at `docs/archive/CLAUDE-original.md`. |

## 2. Completed and accepted tasks

| Date | Task | Accepted? | Commit |
|---|---|---|---|
| 2026-11-05 | Review, finalize, and verify the PostgreSQL Compose service (loopback binding, healthcheck, naming, persistence, password login) | **Accepted**, learning level | `f822332` |
| 2026-11-06 | Phase 0 Task 1: move app into `app/` package, health router | **Accepted** | `dc36d83` |
| 2026-11-06 | Phase 0 Task 2: typed settings (`core/config.py`, `.env.example`) | **Accepted** | `0b4207f` |
| 2026-11-06 | Phase 0 Task 3: async engine, per-request session (`get_db`), `/health/db` | **Accepted**, learning level | see git log |

Non-implementation work done (not "accepted tasks"):
- 2026-11-04: Repository audit.
- 2026-11-04: Instruction files restructured. No application or infrastructure files were touched.
- 2026-11-04/05: Project skills (`teach-and-implement`, `project-review`, `debug-systematically`, `architecture-review`) and `.claude/SAFETY.md` created.

## 3. Current task

**Phase 0 Task 4:** Alembic async setup, the `Student` model, and the first migration.

- **Story points:** **Unresolved.** No points have been assigned.

### Historical allocation (context only, not a current assignment)
- The user was previously given about **6 story points** for backend and database work, at about **4 hours per story point** (from the original brief, §10). How these map to current tasks is **unresolved**.

## 4. Open issues

Each issue lists the decision that tracks it in `docs/engineering-decisions.md`.

| # | Issue | Type | Tracked in |
|---|---|---|---|
| I-2 | Development uses the `postgres` superuser. This is intentional for the learning environment (D-103 Accepted). **Before any deployment**, separate least-privilege owner/migration and runtime roles are required. | Production requirement | D-103 |
| I-3 | pgAdmin is not in `compose.yaml` | Missing component | D-109 |
| I-5 | `.gitignore` does not ignore `__pycache__/` (a `main.cpython-314.pyc` exists) | Git hygiene, fix before first commit | D-111 |
| I-6 | Whether to commit `.vscode/` (and `.claude/`) is undecided | Git hygiene | D-111 |
| I-7 | `requirements.txt` is a full freeze, not direct dependencies. It includes `fastapi-cloud-cli` and `sentry-sdk`. It also cannot capture Conda-installed tools such as `psql` (`postgresql=17`). | Dependencies / data privacy | D-110 |
| I-10 | The engine is never disposed at shutdown. Add `await engine.dispose()` in a FastAPI `lifespan` handler (decided: later). | Robustness | D-113 |
| I-9 | In production, the database port must not be published. On Linux, Docker's published ports bypass ufw through iptables rules. | Production requirement | D-051 |

### Resolved issues
- **I-1** (2026-11-05): name mismatch. `container_name` was removed and the database was renamed to `dormops_db` (D-101).
- **I-4** (2026-11-05): `postgres:17` pin and data path reviewed and accepted (D-050).
- **I-8** (2026-11-06): `.env.example` added (`0b4207f`).

## 5. Open decisions (summary)

All are **Open** with no answer assumed. Details are in `docs/engineering-decisions.md`:
project name (D-100), frontend repository layout (D-102), Redis/Celery (D-104), questionnaire storage (D-105), repository layer (D-106), refresh tokens (D-107), CI platform (D-108), pgAdmin (D-109), dependency management (D-110), `.gitignore`/`.vscode` (D-111), branching/PR workflow (D-112).

## 6. Next implementation step (exactly one)

Phase 0 Task 4 (see §3): Alembic with the async template, the `Student` model, and the first migration.
