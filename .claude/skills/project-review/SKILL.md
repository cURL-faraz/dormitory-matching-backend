---
name: project-review
description: Standalone, read-only code review of specific files, a directory, or the uncommitted changes in this project, graded by severity (Blocker/Major/Minor/Informational) against the project's requirements and security rules. Use only when the user explicitly asks for a code review, audit, or pre-commit review of named code that is independent of the current mentoring task in PROGRESS.md, e.g. "do a code review of compose.yaml", "review the diff before I commit", "audit app/db for security issues". Do NOT use when the user submits work for the current teach-and-implement task, such as "I filled in the TODOs" or "here's my implementation for the current task", and do NOT use for a pre-commit review that involves the current task's code. teach-and-implement (Stages 8–11) handles both. Do not use for conceptual questions or for writing code.
argument-hint: "[files, directory, or 'diff'; default: all uncommitted changes]"
---

# Project Code Review

A standalone, senior-level code review of this repository, done the way CLAUDE.md Phase F describes. **It is read-only and it does not replace the teach-and-implement workflow.**

Review target: $ARGUMENTS

## Boundaries

- **No mentoring authority.** This skill must never:
  - declare a mentoring task accepted or completed;
  - modify `PROGRESS.md`;
  - modify `docs/engineering-decisions.md`.
  
  It may *suggest* changes to those documents, worded as suggestions. All actual updates, and all task acceptance, belong to teach-and-implement (Stages 10–11). If the reviewed code belongs to the current task in PROGRESS.md, say so at the end and point back to that workflow.
- **Pre-commit reviews only for independent code.** Before a pre-commit review, compare the changed files with the current task in PROGRESS.md. If any of the changes belong to the current mentoring task, don't run this review. Tell the learner that the work belongs in teach-and-implement, whose Stages 8–11 cover review, verification, acceptance, and commit preparation, and continue there. If the changes are mixed, offer to review only the independent files.
- **Never modify files or rewrite code**; describe the correction and let the learner make it (CLAUDE.md: the learner writes the code).
- **Safety:** follow **`.claude/SAFETY.md`**, the canonical safety and permission rules, including its secret, personal-data, and log-redaction rules. Rules specific to this skill:
  - **Review with Tier 1 (read-only) commands only.** This skill **must not execute Tier 2, Tier 3, or Tier 4 actions under any circumstances** (e.g. tests, SQL, HTTP requests, container commands, experiments, destructive commands), **even if the learner grants permission** individually or through a session-scoped grant (SAFETY.md §3). If the review needs evidence that only such an action could provide, explain exactly what evidence is missing and why it matters. Then ask the learner to provide it, for example by running the command themselves and sharing the redacted output, or to handle it outside the review, for example through debug-systematically or teach-and-implement.
  - **Never run state-changing experiments (Tier 3)** as part of a review. Investigating behavior belongs to debug-systematically, or to teach-and-implement for the current task.
  - **A committed or hardcoded secret is a finding.** Report its `file:line` location, never its value.

## Step 1: Define the scope
- Work out the target from `$ARGUMENTS`:
  - specific files or directories;
  - `diff`;
  - or, by default, all uncommitted changes.
- **`diff` and the default scope include untracked files.** `git diff` alone does not show them, so run `git status --short` first.
  - Review modified (`M`), added (`A`), and renamed files through `git diff` / `git diff --cached` **plus** the surrounding file.
  - Read relevant untracked (`??`) files explicitly, in full.
  - For deleted (`D`) files, inspect the deletion diff (`git diff -- <path>` / `git diff --cached -- <path>`). Then search the remaining code for anything that still depends on what was removed: imports, callers, routes and routers, Compose service, volume, or network names, settings and environment variable names, migrations, and tests. A dangling reference is a finding.
  - Skip generated or irrelevant untracked files such as `__pycache__/`, `.DS_Store`, and editor state. List them under "not reviewed". If one *should* be ignored but isn't, that is a finding.
  - Never open `.env` or other secret files to review their values. Only confirm that they are git-ignored.
- While the repository has no commits, every non-ignored file counts as uncommitted.
- If the target is ambiguous or very large, propose a scope and ask before reviewing.

## Step 2: Load context
- Read `PROGRESS.md` (the checkpoint, current task, and known open issues) and `docs/engineering-decisions.md`.
- Read the parts of `docs/requirements.md` and `docs/tech-stack.md` that are relevant to the code under review.
- Don't report a **Given** or **Accepted** decision as a defect. If it carries a real risk, report it as Informational and reference its D-number. An issue that is already listed in PROGRESS.md should be marked "known (I-n)" rather than presented as new.

## Step 3: Inspect the real code and its dependencies
- Read the full files, not just pasted snippets or diff hunks.
- Follow what the code depends on and what depends on it: imports and callers, settings and the environment variables they expect (**names only**), Compose services and volumes, schemas and models, and tests.
- Use read-only checks to confirm behavior where you can. Each finding must say whether it was confirmed this way or reasoned from reading.

## Step 4: Review the dimensions that apply
Go through each dimension below. Skip any that don't apply to this code, and list the skipped ones in the scope section.
- **Correctness:** does it do what the task or requirement says?
- **Edge cases:** empty, duplicate, or malformed input; boundaries; concurrency.
- **Security and privacy (always check):**
  - Secrets: hardcoded, committed, or logged.
  - Password hashing; never the national ID as a password.
  - Role taken only from the trusted record.
  - Dormitory-level isolation.
  - OTP purpose separation, expiry, and attempt limits; no revealing whether an account exists.
  - SQL injection and input validation.
  - PII in logs or errors.
  - **No student data sent to external services**, including through dependencies.
  - Network exposure (ports, admin tools).
  - Least-privilege database accounts.
- **Architecture (local scope):** module dependency direction, separation of concerns (matching vs auth vs CRUD), unjustified abstractions, and consistency with the decisions log, **as they show up in the reviewed files and their immediate dependencies**. Report genuine local design problems as normal findings. Don't skip a defect because it is architectural. If a concern is system-wide (component responsibilities, boundaries, dependency direction, or overall structure across the system), note it briefly with its evidence and refer it to architecture-review, rather than evaluating it here.
- **Error handling:** failures surfaced vs swallowed, safe error messages, correct status codes.
- **Reliability:** transactions and rollback, all-or-nothing imports, idempotency, data persistence (volumes), restarts and health checks, resource cleanup.
- **Performance** (only where it realistically matters): N+1 queries, connection pooling, unbounded queries, blocking calls in async code.
- **Maintainability:** clarity, naming, duplication, configuration hygiene.
- **Tests:** whether tests exist, whether they cover failure and negative cases, and whether they are isolated.

## Step 5: Classify each finding
Each finding gets a **kind**, a **severity**, and a **certainty**.

**Kind** (what sort of issue it is):
- **Defect:** the code does something wrong.
- **Requirement violation:** the code breaks a rule in `docs/requirements.md`, CLAUDE.md §2, or a Given or Accepted decision.
- **Architectural risk:** the code works now, but the design will cause problems as the system grows.
- **Future improvement:** a later-phase concern or an optional enhancement. **Always Informational.**

**Severity:**

| Severity | Meaning |
|---|---|
| **Blocker** | Must fix before the work is accepted or committed. Covers wrong behavior, data loss, a security or privacy violation, or breaking a Given requirement. |
| **Major** | Likely to cause failures under realistic conditions, or a design problem that will be costly to undo later. Fix within the current task. |
| **Minor** | Limited impact, or a robustness or clarity improvement. Fix when convenient. |
| **Informational** | No action needed now. Covers observations, future-phase considerations, and learning notes. |

**Certainty:**

| Certainty | Meaning |
|---|---|
| **Verified** | Confirmed by reading the code together with a check, its output, or the documentation. |
| **Possible risk** | Plausible, but depends on conditions you could not confirm. State how to verify it. |
| **Assumption-dependent** | Depends on an Unresolved decision or on unknown context. Name the assumption. |

### Finding discipline
- A Blocker must be **Verified**. If you can't confirm it, it isn't a Blocker. Downgrade it, mark it Possible risk, and say exactly how to confirm it.
- **Don't inflate the report.**
  - Leave out purely speculative problems: if you can't describe a realistic failure scenario, it isn't a finding.
  - Leave out personal stylistic preferences.
  - Report style only when it hurts readability or correctness, and group any remaining nitpicks into a single Minor item.
- Observations about future phases (e.g. "this will need a health check once the backend depends on it") are always **Informational**, never Major or Blocker.
- Prefer a few precise, actionable findings over many weak ones.

## Step 6: Write each finding in this format
```
### [B1] <short title> (Blocker · Defect · Verified)
- **Location:** `path/to/file:line` (or a line range)
- **Problem:** what is wrong, specifically.
- **Why it matters:** the impact, explained intuitively for a learner.
- **Failure scenario:** a concrete, realistic sequence of events that leads to the failure.
- **Recommended correction:** the direction of the fix and the reasoning. Use a minimal snippet only if the fix is hard to describe in words, never a rewrite.
- **How to verify the fix:** a command, test, or observable behavior.
```
Use the IDs B1…, M1…, m1…, I1… for Blocker, Major, Minor and Informational, ordered by severity.

## Step 7: Write the report
1. **Scope and context:** the files reviewed (tracked and untracked), the docs consulted, the commands run, the dimensions skipped and why, and what was **not** covered (e.g. runtime behavior that wasn't executed, files outside the scope, skipped untracked files).
2. **Findings:** in the format above, ordered by severity.
3. **If there are no findings,** say so clearly, e.g. "No findings at any severity in the reviewed scope." Then restate the scope and its limitations: a clean review is not proof of correctness.
4. **Summary:** the count for each severity, a one-line assessment of the code's state (e.g. "Not ready to commit: 1 Blocker"), and the main risk. This is never a task acceptance.
5. **Suggested document updates (optional):** proposed PROGRESS.md issues or decision-log entries, worded as suggestions for teach-and-implement to apply.
6. **Recommended next action:** exactly one. If the code belongs to the current task, this is usually to fix the Blockers and then continue in teach-and-implement.
7. Optionally, ask the learner one question about why they made a particular choice, to build engineering judgment.
