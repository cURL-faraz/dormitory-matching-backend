# Project Progress

> **Read this at the start of every session, before anything else.**
> **Update it** when a task is accepted, when the current task changes, when an issue is found or resolved, and at the end of any session that changed the project's state.
> Keep the past (history), what was checked (verified facts), and what was chosen (decisions) separate. Unknowns stay marked **Unresolved**. Never fill them with assumptions.

_Last updated: 2026-11-05_

---

## 1. Current checkpoint (verified 2026-11-05)

**Coding checkpoint:** a minimal FastAPI application with a working `/health` endpoint, plus a reviewed and verified PostgreSQL service in Docker Compose. PostgreSQL is **not** connected to the application yet.

| Area | Verified state |
|---|---|
| Application code | `main.py` at the repository root: `app = FastAPI()` and `GET /health` → `{"status": "healthy"}` (handler `health_check`). There is no package structure yet. |
| Docker Compose | `compose.yaml` has one `db` service, **reviewed and accepted** on 2026-11-05: `postgres:17` (17.11 at the time), ports `"127.0.0.1:5432:5432"` (loopback only), `POSTGRES_DB: dormops_db`, `POSTGRES_USER: postgres` (development only, D-103), `POSTGRES_PASSWORD` from `.env` with `${…:?}` fail-fast, a `pg_isready` healthcheck over TCP (D-052), and the named volume `postgres_data`. No `container_name`. |
| Database runtime | Container `dormitory-matching-backend-db-1` was started and verified `(healthy)`. Startup takes about 3 s, most of which is the healthcheck interval. The volume `dormitory-matching-backend_postgres_data` holds the initialized cluster. Persistence across `down`/`up` was verified. |
| Database access | From the Mac: `psql -h 127.0.0.1 -p 5432 -U postgres -d dormops_db` works with the password (the connection arrives from `172.18.0.1`, so the `scram-sha-256` rule applies); a wrong password is rejected. Port 5432 is refused on the Wi-Fi IP. |
| DB client tools | `psql` 17.10 (Conda package `postgresql=17`, `defaults` channel) in the project Conda env. It is a development tool and is not visible to pip. |
| Secrets | `.env` exists and defines `POSTGRES_PASSWORD`. It is git-ignored. There is no `.env.example`. |
| Python env | Conda env `dormitory-matching-backend`, Python 3.14.8 |
| Git | Branch `main`, **no commits**. Remote `origin` → `github.com/cURL-faraz/dormitory-matching-backend` |
| Docs | CLAUDE.md restructured into CLAUDE.md, `docs/` and this file (2026-11-04). The original is at `docs/archive/CLAUDE-original.md`. |

## 2. Completed and accepted tasks

| Date | Task | Accepted? | Commit |
|---|---|---|---|
| 2026-11-05 | Review, finalize, and verify the PostgreSQL Compose service (loopback binding, healthcheck, naming, persistence, password login) | **Accepted**, learning level | Pending |

Non-implementation work done (not "accepted tasks"):
- 2026-11-04: Repository audit.
- 2026-11-04: Instruction files restructured. No application or infrastructure files were touched.
- 2026-11-04/05: Project skills (`teach-and-implement`, `project-review`, `debug-systematically`, `architecture-review`) and `.claude/SAFETY.md` created.

## 3. Current task

**Close-out of the accepted Compose task:** Git hygiene (D-111) and the first commit. After that, the next implementation step in §6.

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
| I-8 | There is no `.env.example` to document the required variables | Config | (none yet) |
| I-9 | In production, the database port must not be published. On Linux, Docker's published ports bypass ufw through iptables rules. | Production requirement | D-051 |

### Resolved issues
- **I-1** (2026-11-05): name mismatch. `container_name` was removed and the database was renamed to `dormops_db` (D-101).
- **I-4** (2026-11-05): `postgres:17` pin and data path reviewed and accepted (D-050).

## 5. Open decisions (summary)

All are **Open** with no answer assumed. Details are in `docs/engineering-decisions.md`:
project name (D-100), frontend repository layout (D-102), Redis/Celery (D-104), questionnaire storage (D-105), repository layer (D-106), refresh tokens (D-107), CI platform (D-108), pgAdmin (D-109), dependency management (D-110), `.gitignore`/`.vscode` (D-111), branching/PR workflow (D-112).

## 6. Next implementation step (exactly one)

**A hands-on `psql` session against the running development database** (roadmap Phase 1, items 1–2, 8, 10–11): server vs. database vs. schema vs. table, roles and privileges, and read-only inspection (`\l`, `\dn`, `\dt`, `\du`, `\conninfo`, basic `SELECT`). It is the foundation for pgAdmin (D-109) and for the Phase 2 database code. This step does **not** include SQLAlchemy, Alembic, or app-to-database connection code.
