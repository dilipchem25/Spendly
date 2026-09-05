# Spec: Profile

## Overview
This feature replaces the `/profile` placeholder with a real logged-in account page. It lets an authenticated user view their account details (name, email, member since) and update their name or password. It exists at this stage of the Spendly roadmap to give users a home for account management before expense tracking (create/edit/delete) is built in later steps — it does not touch the `expenses` table or show any expense data.

## Depends on
- Step 2/3 (registration, login, logout) — session-based auth (`session["user_id"]`, `session["user_name"]`) must already work, since this page is only reachable when logged in.

## Routes
- `GET /profile` — view account details (name, email, member since) and show the update forms — logged-in only, redirects to `/login` if not authenticated
- `POST /profile` — update the user's name — logged-in only
- `POST /profile/password` — change the user's password (requires current password) — logged-in only

## Database changes
No database changes. `users` table already has `name`, `email`, `password_hash`, `created_at` (`database/db.py`). New functions needed in `database/db.py` (no schema change):
- `get_user_by_id(user_id)` — fetch a single user row by id
- `update_user_name(user_id, name)` — parameterised `UPDATE users SET name = ? WHERE id = ?`
- `update_user_password(user_id, password_hash)` — parameterised `UPDATE users SET password_hash = ? WHERE id = ?`

## Templates
- **Create:** `templates/profile.html` — account info + "Update name" form + "Change password" form
- **Modify:** none (`base.html` nav already links to `profile`/`logout` when `session.user_id` is set — no change needed)

## Files to change
- `app.py` — add a `login_required` helper/decorator, implement `/profile` (GET/POST) and `/profile/password` (POST), remove the placeholder `profile` route
- `database/db.py` — add `get_user_by_id`, `update_user_name`, `update_user_password`

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash` / `check_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Add a `login_required` guard (redirect to `/login` with a flash message) rather than duplicating the session check in every view
- Changing password requires the current password to be verified with `check_password_hash` before hashing and saving the new one
- Re-use the existing `flash` + `.flash` styling for success/error messages, and the existing `.auth-error` pattern for inline form errors where applicable

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login`
- [ ] Visiting `/profile` while logged in shows the current name, email, and member-since date
- [ ] Submitting the name-update form with a valid name updates it and is reflected immediately in the page and in the navbar
- [ ] Submitting the name-update form with an empty name shows a validation error and does not update the database
- [ ] Submitting the password-change form with the correct current password and a valid new password updates `password_hash` (verify by logging out and back in with the new password)
- [ ] Submitting the password-change form with an incorrect current password shows an error and does not update the database
- [ ] The old placeholder text `"Profile page — coming in Step 4"` no longer appears anywhere
- [ ] App starts without errors and all other existing routes (`/`, `/register`, `/login`, `/logout`, `/terms`, `/privacy`) still work
