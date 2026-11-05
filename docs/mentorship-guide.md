# Mentorship Guide: Detailed Teaching Reference

> **Source:** section 6.2–6.4 detail of the original CLAUDE.md, moved word for word (archived at `docs/archive/CLAUDE-original.md`). The rules themselves are summarized in CLAUDE.md, and they are binding. This file holds the full examples and concept checklists.
> **Read this:** before teaching a new concept (Phase B); before proposing a project or directory structure (Phase C); before writing a template with deliberate blanks (Phase D); and specifically before the first lesson on `database.py`, engines, sessions, or ORM models.

## 6.2 Phase B: Teach the concepts from scratch

Teach the concepts that are necessary for the upcoming implementation.

For example, before creating `database.py`, explain:

### Database URL

- What a database URL represents.
- Its components: dialect, driver, username, password, host, port, and database name.
- Why SQLAlchemy uses this structure.
- What the difference is between `postgresql://` and `postgresql+asyncpg://`.
- How environment variables and Pydantic Settings fit into configuration management.
- Why credentials should not be hardcoded.

### SQLAlchemy Engine

- What an engine actually represents.
- Why we need it.
- Whether it establishes a database connection immediately or manages connections lazily.
- What a connection pool is.
- How the engine interacts with PostgreSQL.
- Why we generally create one application-level engine rather than one engine per request.

### Session and AsyncSession

- What a database session represents.
- How it differs from an engine and an individual connection.
- Why sessions are needed.
- What `sessionmaker` or `async_sessionmaker` does.
- How the session lifecycle works during an HTTP request.
- What `commit`, `rollback`, `flush`, and `refresh` mean.
- Why sessions should not be shared indiscriminately between concurrent requests.
- How FastAPI dependencies can provide and clean up sessions.

### Declarative ORM Models

- What ORM means.
- How Python classes map to relational tables.
- What `DeclarativeBase` does.
- How `Mapped` and `mapped_column` work in SQLAlchemy 2.x.
- What the older `declarative_base()` function did.
- Why models should not depend on HTTP request objects.
- How foreign keys, constraints, relationships, and indexes are represented.

Explain the role of each concept and how the pieces interact.

Do not merely define the methods. Explain the lifecycle and architecture.

## 6.3 Phase C: Explain file responsibilities and project structure

Before creating files, propose the structure and justify it.

For example, if you suggest:

```text
app/
├── main.py
├── core/
│   └── config.py
├── db/
│   ├── database.py
│   └── models.py
├── schemas/
├── api/
├── services/
└── ...
```

Explain:

- Why each directory exists.
- What belongs in each file.
- Which modules may depend on which other modules.
- Which dependencies should be avoided.
- How the structure helps testing, maintenance, and collaboration.
- How it can evolve as the application grows.

Do not create unnecessary abstraction layers.

Avoid introducing repositories, generic base classes, factories, or other design patterns without explaining the actual problem they solve.

The objective is a maintainable architecture, not maximum file count.

## 6.4 Phase D: Provide implementation templates with deliberate blanks

This is essential.

I want to write the code myself.

Provide templates with empty places, incomplete expressions, TODOs, or deliberately omitted implementation details.

For example, when introducing a database URL:

```python
DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{________}:{________}@{________}:{________}/{________}"
)
```

When introducing the engine:

```python
engine = create_async_engine(
    ________,
    echo=________,
    pool_size=________,
)
```

These are illustrative templates. Adapt them to the actual implementation and explain which values I should choose.

Do not reveal every answer immediately.

For each template:

1. Explain the imports and why they are required.
2. Explain what each function or class is responsible for.
3. Explain what I need to fill in.
4. Explain how to reason about the missing values.
5. Give me the implementation task.
6. Let me attempt it before providing a complete solution.

Use this approach for every relevant file and implementation stage.

If a particular syntax is difficult to infer, give me a smaller example or a hint rather than immediately filling everything in.
