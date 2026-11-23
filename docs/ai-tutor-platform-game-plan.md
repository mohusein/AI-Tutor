# AI Tutor Platform — Product Scope and Game Plan

## Product scope

The tutor teaches only:

- **SQL statements:** writing, reading, and debugging SQL queries such as SELECT/WHERE, JOIN, and GROUP BY.
- **Python coding:** writing, reading, and debugging Python code, beginning with variables, conditions, loops, functions, and lists.

For requests outside these areas, the tutor should briefly explain its scope and redirect the student to SQL or Python coding.

## Individual student accounts

Each learner creates an account with a unique email address and their own password. There are no shared classroom credentials. The app hashes passwords with Argon2, issues a short-lived signed access token, and associates saved progress with the authenticated user ID. Students can only read or update their own progress.

Account recovery, email verification, teacher accounts, and classroom administration are future work. Do not create real student accounts until the student has chosen their own credentials through the app.

## First release

- Register, sign in, and sign out.
- Browse SQL and Python lessons.
- Ask lesson-scoped questions and receive step-by-step hints.
- Mark lessons complete and return to personal saved progress.

## Architecture

```text
React frontend
  └── Python FastAPI backend
        ├── SQLite for local development
        ├── Argon2 password hashing and signed access tokens
        └── OpenAI Responses API, called only by the backend
```

The OpenAI API key belongs in the backend's local `.env` file or deployment secret store. Never put it in frontend code or commit it. Tutor conversation text is sent to OpenAI for a reply, kept in browser memory for the current session, and not saved in the app database.

## Current implementation milestones

1. **Accounts:** Individual registration and login with private per-user progress.
2. **SQL/Python lesson path:** Starter lessons for SQL SELECT/WHERE, JOIN, GROUP BY, and Python variables, control flow, functions, and lists.
3. **Tutor chat:** Authenticated lesson chat with bounded messages and SQL/Python-only tutor instructions.
4. **Next:** Add hands-on exercises and submission feedback for SQL and Python.

## Before serving students

This is an early development build. Before deployment, add account recovery, email verification, database migrations, production database/HTTPS configuration, rate limits, and a student-facing privacy notice. Review privacy and legal requirements for the audience and locations served, especially if learners may be children. Do not store chat history until there is a clear retention and deletion policy.
