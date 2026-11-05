# Engineering Decisions Log

> **Read this:** before making or proposing any architectural or design decision (schema, auth, structure, infrastructure, dependencies, tooling); before reopening a topic, to check whether it is already decided; and whenever an "Open" decision below becomes relevant to the current task.
> **Update this:** whenever a decision is proposed, accepted, superseded, or rejected. Never mark a decision Accepted unless the user agreed to it.

## Status meanings

| Status | Meaning |
|---|---|
| **Given** | Fixed by the project brief (original CLAUDE.md). It is a requirement, not something we chose during mentoring. It can only change if the user changes the requirements. |
| **Accepted** | Discussed and explicitly agreed by the user during mentoring. |
| **In repo, unreviewed** | Already present in the repository but not yet reviewed or justified. Do not treat it as accepted. |
| **Open** | Not decided. Do not assume an answer. Raise it when it becomes relevant. |
| **Superseded / Rejected** | Kept for history. |

## Entry template

```markdown
### D-NNN: <title>
- **Status:** Given | Accepted | In repo, unreviewed | Open | Superseded by D-NNN | Rejected
- **Date:** YYYY-MM-DD (date recorded or last changed)
- **Context / problem:**
- **Alternatives:**
- **Trade-offs:**
- **Decision:** (or "None yet" if Open)
- **Rationale:**
- **Consequences:** (what this enables, constrains, or makes us do later)
- **Scope:** project-specific | broadly reusable
```

---

## Given (from the project brief)

### D-001: Start as a modular monolith
- **Status:** Given
- **Date:** 2026-11-04 (recorded)
- **Context / problem:** The architecture needs a starting shape.
- **Alternatives:** Modular monolith; microservices.
- **Decision:** Begin with a modular monolith unless a concrete requirement justifies something else.
- **Rationale:** Stated in the brief (original §7). A full trade-off explanation has not been taught yet.
- **Consequences:** One deployable backend with clear internal module boundaries.
- **Scope:** Broadly reusable default.

### D-002: Core technology stack
- **Status:** Given
- **Date:** 2026-11-04 (recorded)
- **Decision:** Backend: FastAPI, PostgreSQL, SQLAlchemy 2.x (async, asyncpg), Alembic, Pydantic 2, pydantic-settings, JWT, pytest + HTTPX. Frontend: Next.js, React, TypeScript, MUI (not Tailwind), RTL, Zustand, TanStack React Query. Infra: Docker, Docker Compose. Full detail is in `docs/tech-stack.md`.
- **Consequences:** Redis and Celery are **not** decided. See D-104.
- **Scope:** Project-specific.

### D-003: Student data stays inside the university network
- **Status:** Given
- **Date:** 2026-11-04 (recorded)
- **Decision:** Production student data must not be sent to external services. Deployment is on university-owned infrastructure.
- **Consequences:** This constrains SMS/OTP providers, logging/monitoring/error-tracking services, CI handling of data, and any SaaS tooling. Every dependency that phones home must be reviewed. See D-110.
- **Scope:** Project-specific.

### D-004: Authentication flow (initial agreed design)
- **Status:** Given
- **Date:** 2026-11-04 (recorded)
- **Decision:** Students log in with their student number. The initial password is based on the registered mobile number, never the national ID. First login forces a restricted OTP-verified password change. The role comes only from the trusted account record. Normal login does not require OTP unless the requirements change. See `docs/requirements.md` §3.2–3.3.
- **Scope:** Project-specific.

---

## Accepted (during mentoring)

### D-050: PostgreSQL via the official Docker image, major-version tag `postgres:17`
- **Status:** Accepted
- **Date:** 2026-11-05
- **Context / problem:** We need a local PostgreSQL server for development, with data that survives container removal.
- **Alternatives:** A floating `latest` tag; a major-version tag (`17`); an exact minor version or digest (e.g. `17.11`, `@sha256:…`); upgrading to 18.
- **Trade-offs:** `postgres:17` follows 17.x minor releases (bug and security fixes, same on-disk format, safe to swap over an existing volume), and it only moves on `pull`. An exact pin is more reproducible but needs manual updates. A major upgrade changes the on-disk format (an 18 server cannot read a 17 data directory), and the 18 image also moved its data path.
- **Decision:** Use `postgres:17` with the named volume `postgres_data` mounted at `/var/lib/postgresql/data`. Version 17.11 was resolved on 2026-11-05.
- **Rationale:** It is good enough for development: automatic minor fixes, no surprise major upgrades.
- **Consequences:** Major upgrades must be deliberate, using `pg_dump`/restore or `pg_upgrade`, never a blind tag bump. Client tools are kept on the same major version (`postgresql=17` in Conda). Production should pin the exact minor version or digest.
- **Scope:** Broadly reusable.

### D-051: Publish the database port on loopback only
- **Status:** Accepted
- **Date:** 2026-11-05
- **Context / problem:** `"5432:5432"` binds on all interfaces, exposing a superuser login to any device on the same network.
- **Alternatives:** All interfaces (`5432:5432`); loopback only (`127.0.0.1:5432:5432`); not publishing the port at all.
- **Trade-offs:** All interfaces exposes the database to the network. Not publishing it blocks host tools such as `psql` on the Mac. Loopback only allows host tools but not other devices.
- **Decision:** `"127.0.0.1:5432:5432"`.
- **Rationale:** The listener exists only on `lo0`, so packets arriving on the Wi-Fi interface are refused by the macOS kernel and never reach Docker. This was verified with `lsof` (`127.0.0.1:5432`) and `nc` (refused on the Wi-Fi IP). The macOS application firewall is per-application, so Docker Desktop (signed software) could be auto-allowed; the binding is the real control.
- **Consequences:** Containers on the Compose network still reach `db:5432` directly, which does not use the published port. It covers IPv4 only, so use `127.0.0.1` rather than `localhost` in host connection strings. **Production:** do not publish the database port at all, because on Linux Docker's iptables rules bypass ufw (I-9).
- **Scope:** Broadly reusable.

### D-052: PostgreSQL healthcheck
- **Status:** Accepted
- **Date:** 2026-11-05
- **Context / problem:** "Container running" does not mean "Postgres is accepting connections". Dependent services need a readiness signal.
- **Alternatives:** No healthcheck; `CMD` with literal values; `CMD-SHELL` with variables read from the container's environment.
- **Trade-offs:** `CMD` avoids the shell but duplicates the user and database names, which can drift apart. `CMD-SHELL` keeps one source of truth (`environment:`) but relies on `/bin/sh` and the `$$` escape.
- **Decision:** `["CMD-SHELL", "pg_isready -h 127.0.0.1 -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]`, with `interval: 10s`, `timeout: 3s`, `retries: 5`, `start_period: 30s`, `start_interval: 2s`.
- **Rationale:** `-h 127.0.0.1` forces TCP, so the check cannot pass against the image's temporary initialization server, which listens only on the Unix socket. `$$` defers expansion from Compose to the container shell. `CMD-SHELL` takes exactly one string. A measured startup of about 3 s makes 30 s a safe margin.
- **Consequences:** A future backend uses `depends_on: db: condition: service_healthy`, which gates startup only. "Healthy" does **not** prove the password, the database name, the schema, or host reachability, because `pg_isready` does not authenticate. The application still needs its own reconnect handling.
- **Scope:** Broadly reusable.

### D-101: Development database name
- **Status:** Accepted
- **Date:** 2026-11-05
- **Decision:** `dormops_db`.
- **Rationale:** An underscore instead of a hyphen, so the name never needs quoting in SQL.
- **Consequences:** This does **not** decide D-100 (project name). The Compose project name currently comes from the folder (`dormitory-matching-backend`), which produces `dormitory-matching-backend-db-1` and `dormitory-matching-backend_postgres_data`. The container name is generated by Compose (no `container_name`).
- **Scope:** Project-specific.

### D-103: Database roles and least privilege
- **Status:** Accepted (learning environment)
- **Date:** 2026-11-05
- **Context / problem:** `POSTGRES_USER: postgres` is the superuser. The brief requires least-privilege database accounts.
- **Alternatives:** The superuser for everything; separate owner/migration and runtime roles from the start.
- **Trade-offs:** A superuser bypasses all permission checks. It can read and change everything, manage roles and databases, bypass row-level security, read server files, and run OS commands through `COPY … PROGRAM`, so an SQL injection becomes a full compromise. Separate roles cost setup and migration complexity.
- **Decision:** The local development environment intentionally uses `postgres`. This is not a configuration defect.
- **Rationale:** It keeps Phase 1 focused on fundamentals. The environment holds no real student data and is reachable only from the Mac (D-051).
- **Consequences:** **Before any deployment**, production requires an owner/migration role (DDL in its schema, used by Alembic) and a runtime role for the app (`SELECT`/`INSERT`/`UPDATE`/`DELETE` on app tables and `USAGE` on sequences, with no DDL, no role or database management, and no server-file or program access). `postgres` is for administrators only. Tracked as I-2.
- **Scope:** The principle is broadly reusable; the timing is project-specific.

---

## Open decisions

### D-100: Project name
- **Status:** Open
- **Context:** The repository is `dormitory-matching-backend`. The development database is `dormops_db` (D-101), but that does not settle the project name. The Compose project name currently comes from the folder name. The earlier `dormpos-db`/`dormops-db` mismatch was resolved on 2026-11-05 (I-1).
- **Decision:** None yet. Do not invent one.

### D-102: Frontend repository layout
- **Status:** Open
- **Context:** The repository is named `...-backend`, but the project is full-stack.
- **Alternatives:** A separate frontend repository; a folder in this repository; renaming the repository to a monorepo.
- **Decision:** None yet.

### D-104: Background processing (Redis + Celery)
- **Status:** Open
- **Context:** The brief says to evaluate this for matching and import workloads and not to add it without a concrete need.
- **Decision:** None yet. This will be evaluated in roadmap Phase 7.

### D-105: Questionnaire storage (JSONB vs relational vs hybrid)
- **Status:** Open
- **Decision:** None yet. This will be decided explicitly in roadmap Phase 3 or 6.

### D-106: Repository layer vs service functions with `AsyncSession`
- **Status:** Open
- **Decision:** None yet. Do not introduce a repository layer without a justified need.

### D-107: Refresh tokens
- **Status:** Open
- **Decision:** None yet. To be decided in roadmap Phase 5.

### D-108: CI platform
- **Status:** Open
- **Context:** The Git remote `origin` points to GitHub (verified). The brief says "GitHub Actions or GitLab CI, depending on repository/team setup". The university team's setup is unknown.
- **Decision:** None yet.

### D-109: pgAdmin in development Compose
- **Status:** Open
- **Context:** The brief lists pgAdmin for development. It is not in `compose.yaml` yet. It must never be exposed in production.
- **Decision:** None yet (whether, and when, to add it).

### D-110: Dependency management
- **Status:** Open
- **Context:** `requirements.txt` is a full freeze (64 packages), not a list of direct dependencies. It includes `fastapi-cloud-cli` and `sentry-sdk`, which can talk to external services. That is relevant to D-003. There is no dev/prod split.
- **Additional context (2026-11-05):** The development tool `psql` was installed with Conda (`postgresql=17`, `defaults` channel). pip cannot see or install it, so `requirements.txt` alone cannot describe this environment. It is a development tool, not an application runtime dependency.
- **Alternatives:** Keep the freeze; maintain a curated direct-dependency file plus a lock or freeze; split dev and prod requirements; a Conda `environment.yml` listing Conda packages (e.g. `postgresql=17`) and pip packages together.
- **Decision:** None yet.

### D-111: Git hygiene: `.gitignore` coverage and `.vscode/`
- **Status:** Open
- **Context:** `.gitignore` contains only `.env`. `__pycache__/` is not ignored. Whether `.vscode/settings.json` is committed is undecided. There are no commits yet.
- **Decision:** None yet. Resolve before the first commit.

### D-112: Branching and pull-request workflow
- **Status:** Open
- **Context:** No commits or branches exist yet. The brief says to teach branching and PRs when they become relevant.
- **Decision:** None yet.
