# Product Requirements: Dormitory Roommate-Matching System

> **Source:** moved word for word from sections 2 and 3 of the original CLAUDE.md (archived at `docs/archive/CLAUDE-original.md`).
> **Read this:** before designing or implementing any domain feature: the database schema, authentication/OTP, student import, dormitory administration, the questionnaire, or matching. Also read it when a request seems to conflict with a product rule.
>
> First-person wording ("I", "me", "my") refers to the project owner (the learner).

# 2. The Actual Project: Dormitory Roommate-Matching System

## 2.1 Project objective

The application helps university dormitory administrators manage student accommodation and perform roommate matching.

The university wants a centralized system where administrators can manage dormitories, import eligible students, collect roommate preferences, execute matching algorithms, and export matching results.

The system will eventually be deployed on university-owned infrastructure.

**Critical infrastructure constraint:** Student information is sensitive. Production student data must remain within the university network and must not be sent to external services.

## 2.2 Main user roles

### Super Admin

- Manages dormitory administrator accounts.
- Can create, retrieve, update, and delete administrator accounts.
- Can manage the system's administrative structure.

### Dormitory Admin

- Can be assigned to multiple dormitories.
- Manages only the dormitories to which they have been assigned.
- Manages eligible students in their dormitories.
- Can initiate or manage matching operations.
- Can inspect and export matching results.

Different dormitories must remain logically isolated. An administrator assigned to one dormitory must not be able to access another dormitory's student data unless explicitly authorized.

### Student

- Does not register independently.
- Has an account provisioned by the system through an administrator's student-import operation.
- Can log in using their student number.
- Initially receives a default password based on their registered mobile phone number.
- Must change that password on their first login.
- Can complete the roommate preference questionnaire.
- Can submit feedback and participate in the matching workflow.

The national ID must never be used as the default password.

---

# 3. Main Product Requirements and User Flows

## 3.1 Student and administrator account provisioning

There is no public signup process.

Students are imported from Excel/CSV files by authorized administrators.

The backend must:

- Parse the uploaded file.
- Validate required columns and values.
- Detect duplicate student numbers.
- Validate dormitory assignments and eligibility.
- Create student accounts.
- Set the initial password according to the specified policy.
- Hash passwords before storing them.
- Handle invalid rows and report meaningful errors.
- Avoid creating partially imported datasets when the import operation fails.

Administrators must be created and managed through the authorized administrative workflow.

## 3.2 Authentication and first-login password change

The agreed initial authentication flow is:

1. The frontend sends login credentials in the request body.
2. The backend identifies the account.
3. It verifies the password against the stored password hash.
4. It checks the account status and determines the user's role.
5. If the account is invalid, it returns an appropriate error.
6. If this is the user's first login, the backend must not grant ordinary application access.
7. Instead, the user enters a restricted password-change flow.
8. The backend sends an OTP to the registered mobile number.
9. The frontend displays the OTP verification page.
10. The backend verifies the OTP and its associated challenge.
11. The user sets a new password.
12. The backend marks the initial password-change requirement as completed.
13. The user can now obtain normal authenticated access.

The backend must determine the role from the trusted account record, never from a client-provided role field.

The frontend is responsible for navigating to the appropriate role-specific page based on the backend response.

## 3.3 OTP and password reset

OTP challenges must be designed carefully.

Consider:

- Challenge identifiers.
- OTP purpose.
- Expiration time.
- Maximum verification attempts.
- Resend restrictions.
- Challenge consumption and reuse prevention.
- Account association.
- Secure OTP storage or verification.
- Rate limiting.
- SMS delivery failures.
- Concurrent requests.

Initial password change and forgotten-password reset must be separate logical purposes.

A challenge created for one purpose must not authorize an operation belonging to another purpose.

The forgotten-password flow must avoid revealing whether an account exists.

Do not assume normal login requires OTP unless the requirements are explicitly changed.

## 3.4 Dormitory administration

Administrators should be able to:

- Create dormitories.
- View dormitories.
- Update dormitory information.
- Delete dormitories where deletion is safe and permitted.
- Manage administrator-to-dormitory assignments.
- View eligible students in their authorized dormitories.

Design this with proper authorization and database constraints.

## 3.5 Student questionnaire

Students will answer a questionnaire containing roommate preferences.

Some questions may evolve over time, so evaluate whether dynamic JSON fields, normalized relational tables, or a hybrid approach is appropriate.

Do not blindly choose JSON because the requirements mention dynamic fields. Explain the trade-offs and make an explicit architectural decision.

## 3.6 Matching algorithm

The matching functionality is conceptually based on:

- Eligibility filtering.
- Same dormitory and same gender constraints.
- Hard incompatibility rules or red lines.
- Weighted compatibility scoring.
- A normalized score from 0 to 100.
- Matching results that administrators can inspect and export.

The matching algorithm should be kept separate from authentication and ordinary CRUD logic.

Evaluate whether background processing with Celery and Redis is justified for matching operations.

Do not introduce infrastructure merely because it is popular. Explain the actual requirement that makes it necessary.
