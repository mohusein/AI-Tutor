# AI Tutor Platform — Junior Developer Game Plan

## Goal

Build a focused learning platform where students can sign in, get guided help from an AI tutor, complete exercises, and return later to continue their saved progress.

Start with one learner group, one subject, and one learning path. For example: high school algebra, beginning with linear equations.

## First release

Students should be able to:

- Create an account, sign in, and recover access.
- Choose a lesson or continue where they left off.
- Ask the tutor questions and receive explanations and hints.
- Complete short exercises and get feedback.
- See saved progress and resume a lesson later.

Define “progress” before building it. A useful first version tracks lesson completion, exercise attempts, scores, and the student’s current position. Collect only the personal information needed to provide the service.

## Suggested architecture

```text
Student web app
    │
    ├── Authentication provider
    │
    └── Backend API
          ├── User, lesson, and progress database
          └── AI provider
```

Call the AI provider from the backend. This keeps its API key out of the browser, gives the team a place to apply tutoring rules and request limits, and helps control what student information is sent.

Choose tools the team already knows. A reasonable starting point is a web framework such as React, a small API in the team’s preferred language, and PostgreSQL. Use a reputable hosted identity provider or a well-maintained framework solution. Don’t build password handling from scratch or store plaintext passwords.

## Initial data model

- **User:** internal ID and account metadata.
- **Lesson:** subject, title, and lesson content or references.
- **Attempt:** user, exercise, answer, feedback, and timestamp.
- **Progress:** user, lesson, completion state, and last position.

Associate every user-owned record with an internal user ID. The backend must verify that the signed-in user is allowed to read or change each record; a user ID supplied by the browser is not proof of ownership.

Decide whether tutor conversations need to be saved. If they are, explain what is retained, limit access, and set a retention policy.

## Development milestones

1. **Product outline:** Agree on the first learner group, subject, lesson path, and definition of progress.
2. **Authentication:** Add registration, sign-in, sign-out, and account recovery with the selected provider.
3. **Lesson experience:** Display lessons and exercises without AI.
4. **Progress saving:** Store completion and attempts; add a “continue learning” view.
5. **Tutor integration:** Add a backend endpoint that sends a lesson question to the AI provider and returns the response.
6. **Tutoring behavior:** Guide students with explanations and hints before revealing answers.
7. **Review and pilot:** Check authorization, error handling, accessibility, and the student experience before inviting a small pilot group.

Keep milestones small and reviewable. For each pull request, describe the change and include a short verification summary or screenshots when useful.

## Privacy and security

- Use HTTPS and secure sessions or the identity provider’s recommended flow.
- Check authorization on every user-specific API route.
- Keep AI keys and other secrets out of source code, browser code, and logs.
- Avoid sending identifying details to the AI provider unless they are essential.
- Explain what data is saved and how a student can request deletion.
- If children may use the platform, consult the organization’s privacy and legal reviewers before collecting data or launching. Requirements depend on the audience and locations served.
- Add rate limits and request-size limits to AI endpoints.

## Pilot measures

Track a small set of outcomes: whether students finish a lesson, return to continue, and improve on later exercises. Prefer aggregate measurements and avoid logging unnecessary student content.

## First deliverable

Write a short product brief and build a working prototype for one lesson. Once students can use it safely and resume their work, expand to more subjects, teacher tools, and richer progress reports.
