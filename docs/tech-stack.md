# Technology Stack and Development Environment

> **Source:** sections 4 and 5 of the original CLAUDE.md, moved word for word (archived at `docs/archive/CLAUDE-original.md`).
> **Read this:** before recommending, adding, or upgrading any dependency or tool; before writing configuration (Docker, settings, env files); and when choosing a library or framework pattern.
>
> Section 5 below is a **historical snapshot** of the environment when the project began. For the current, verified state, see `PROGRESS.md`.

# 4. Technology Stack and Architectural Direction

Use the following stack as the starting point.

## Backend

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- asyncpg
- Alembic
- Pydantic 2
- pydantic-settings
- JWT-based authentication
- Secure password hashing
- pytest and HTTPX for testing

Prefer modern SQLAlchemy 2.x patterns, including typed ORM mappings and `AsyncSession` where appropriate.

When teaching declarative mappings, explain the relationship between the older `declarative_base()` approach and the modern `DeclarativeBase` pattern. Do not use outdated patterns without explaining why.

## Frontend

- Next.js
- React
- TypeScript
- Material UI (MUI), not Tailwind
- Right-to-left (RTL) support
- Zustand where client-side shared state is appropriate
- TanStack React Query for server-state management

The frontend must have a clean separation between authentication, student functionality, and administrative functionality.

The user interface should include:

- Student login.
- Administrator login.
- OTP verification.
- Initial password change.
- Forgotten-password flow.
- Role-specific dashboards.
- Basic dormitory and student administration interfaces.
- Questionnaire and matching-related interfaces.

Explain the purpose of each frontend technology and when it should be used. Avoid unnecessary dependencies.

## Infrastructure and DevOps

- Docker
- Docker Compose
- PostgreSQL container
- pgAdmin for database inspection during development
- Redis if justified by asynchronous/background tasks
- Celery if justified by the matching or import workloads
- GitHub Actions or GitLab CI, depending on repository/team setup
- University self-hosted deployment

Production deployment must respect the university's network and data-isolation requirements.

---

<!-- Historical snapshot: original section 5. Some details are now outdated; see the "Verified environment facts" section below and PROGRESS.md. -->

# 5. Existing Development Environment and Starting Checkpoint

Do not assume we are starting from a completely empty machine.

I already have a Conda environment containing the following relevant packages:

```text
fastapi==0.161.0
SQLAlchemy==2.1.6
alembic==1.20.1
asyncpg==0.32.0
pydantic==2.14.1
pydantic-settings==2.16.1
python-dotenv==1.2.4
uvicorn==0.54.0
httpx==0.28.1
greenlet==3.5.6
```

The full `requirements.txt` is available in the project files. **Read that file before recommending additional packages.**

Do not reinstall packages that are already available unless there is a specific compatibility or security reason.

Before adding dependencies:

1. Inspect the current environment.
2. Identify what is already installed.
3. Identify what is missing.
4. Explain the purpose of each additional package.
5. Check compatibility with the selected stack.
6. Give me the installation commands.

I use Conda, so prefer Conda-compatible instructions and `python -m pip` where appropriate.

## Current application checkpoint

My current application contains:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def read_root():
    return {"status": "healthy"}
```

This endpoint works.

Docker is installed:

```text
Docker version 29.9.2
Docker Compose version v5.6.1
```

Host port `5432` is available.

We are currently at the stage of setting up PostgreSQL using its official Docker image and adding pgAdmin as a graphical database management interface.

We have not yet established a working application-to-PostgreSQL connection.

Continue from this exact checkpoint. Do not restart FastAPI from scratch or assume that PostgreSQL has already been configured successfully.

---

# Verified environment facts (repository audit, 2026-11-04)

These were checked directly against the machine and repository. They **add to** the historical snapshot above and correct it where they differ.

| Fact | Verified value |
|---|---|
| Conda environment name | `dormitory-matching-backend` (`conda activate dormitory-matching-backend`) |
| Python version in that environment | 3.14.8 |
| FastAPI installed in that environment | 0.161.0 (confirmed with `pip show`) |
| Shell default when not activated | Conda `base` (Python 3.13.5), which is **not** the project environment |
| `requirements.txt` contents | A full `pip freeze`-style list (64 pinned packages, including transitive ones). It is not a curated list of direct dependencies. |
| Notable transitive packages in `requirements.txt` | `fastapi-cli`, `fastapi-cloud-cli`, `sentry-sdk`, `opentelemetry-*`, `httpx2`, `httpcore2`, `uvloop`, `python-multipart`, `email-validator`. These most likely came from `fastapi[standard]`, but that is **unverified**. |
| Docker / Compose versions | Docker 29.9.2, Docker Compose v5.6.1 |
| VS Code settings | `.vscode/settings.json` sets Conda as the environment and package manager and `python.terminal.useEnvFile: true` |
| Conda channels (2026-11-05) | `defaults` only. Keep installs on `defaults` to avoid solver conflicts. |
| PostgreSQL server (2026-11-05) | Image `postgres:17`, which resolved to **17.11** (Debian build, aarch64) |
| PostgreSQL client tools (2026-11-05) | `psql` **17.10** from Conda package `postgresql=17` in the project env. It is a development tool, invisible to pip (D-110). Activate the env to use it. |
| Compose-generated names (2026-11-05) | Project `dormitory-matching-backend` (from the folder name). Container `dormitory-matching-backend-db-1`, volume `dormitory-matching-backend_postgres_data`, network `dormitory-matching-backend_default` (observed gateway `172.18.0.1`) |

Discrepancies with the snapshot above:

- The `/health` handler in `main.py` is named `health_check`, not `read_root`. The behavior is the same: it returns `{"status": "healthy"}`.
- `compose.yaml` already exists with a `db` service. The snapshot says Compose setup had not started.
