# Complex Features & Admin Implementation Memo

This document serves as a reminder for implementing complex, high-risk, or easily overlooked features in the MangaAnimEden project.

## 1. Administration & User Roles

### User Hierarchy

We need to strictly differentiate between **Technical Administration** (Django Admin) and **Business Administration** (Site Dashboard).

* **Superuser (Tech God)**:
  * *Access*: Full Django Admin access. Can delete anything, including other admins.
  * *Creation*: `python manage.py createsuperuser` (CLI only).
  * *Capabilities*: Manage DB migrations, sensitive keys, direct DB edits. **Can promote Site Administrators.**

* **Site Administrator (Business Owner)**:
  * *Access*: **Business Level Dashboard** (Custom UI, not Django Admin).
  * *Creation*: Promoted by Superuser (initially via Shell, later via UI).
  * *Capabilities*:
    * **Role Management**: Add/Remove other Admins (limit 5) and Moderators.
    * **Analytics**: View user growth, retention, and engagement stats.
    * **System Config**: Toggles for maintenance mode, feature flags.
    * **User Management**: Ban/Unban, Reset passwords, View user emails.
    * **Content**: Feature/Hide posts, Manage "Home" carousel.

* **Moderator (Community)**:
  * *Access*: Frontend "Mod Tools" only (No Django Admin, No Dashboard).
  * *Creation*: Promoted by Site Administrator.
  * *Capabilities*: Delete chat messages, Time-out users, Pin events/groups.

### Future Business Dashboard Requirements

* [ ] **Dashboard UI**: A dedicated `/admin-panel/` (separate from `/admin/`) using the site's design system.
* [ ] **Role Management UI**: Interface to search users and toggle `is_admin` / `is_moderator` flags.
* [ ] **Audit Logs**: Visual log of who banned who.

### Implementation Checklist

* [ ] ***Role Middleware***: Create a decorator/middleware (e.g., `@requires_role('mod')`) to strictly enforce access on Views.
* [ ] ***Audit Logs***: Every admin action (ban, delete, promote) MUST be logged in a `SystemLog` model with `user`, `action`, `target`, and `IP`.
* [ ] ***Hard vs Soft Bans***: Decide if banning a user deletes their data (GDPR) or just flags `is_active=False`.

## 2. Data Consistency & Integrity (The "Hidden" Complexity)

### Deletion Cascades

* **Groups/Events**: If a Group is deleted, what happens to its Messages?
  * *Policy*: `on_delete=models.CASCADE` might wipe history. Consider `SET_NULL` or Soft Deletion (`is_deleted` field) to preserve chat history for audit.
* **User Deletion**: If a user deletes their account:
  * Do their messages remain? (Usually yes, labeled as "Deleted User").
  * Do their uploaded images get deleted from S3/Media? (Need a signal to cleanup files).

### Concurrency

* **Event Signup**: What if the last spot in an event is taken by two users simultaneously?
  * *Solution*: Use database transactions (`transaction.atomic`) and row locking (`select_for_update`) for critical counts.

## 3. Security & Abuse Prevention

### Uploads

* [ ] **File Validation**: Users might upload `.exe` or corrupted piles named `.png`. Validate MIME types/Magic Bytes, not just extensions.
* [ ] **Storage Quotas**: Prevent one user from filling the disk. Implement per-user usage tracking.

### Spam Protection

* [ ] **Chat Rate Limiting**: Limit messages to X per minute to prevent bot spam.
* [ ] **Report System**: Allow users to report messages. If X reports are received, auto-hide content until review.

## 4. Notifications System

features often forgotten until the end:

* [ ] **Dispatcher**: Centralized service to send Email vs In-App vs Push.
* [ ] **Preferences**: Users need a UI to opt-out of specific notification types (e.g., "Email me only for Security, not Events").
* [ ] **Do Not Disturb**: Logic to queue notifications during night hours if requested.

## 5. Scalability Considerations

* [ ] **Asset Offloading**: Currently media is local (`/media/`). Plan migration to AWS S3 / Cloudinary before production.
* [ ] **Search Index**: `icontains` is slow. Any search bar will eventually need Full Text Search (Postgres SearchVectors or Elasticsearch).
