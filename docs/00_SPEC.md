# MangaAnimEden Specification

## Vision

A comprehensive web platform for manga and anime enthusiasts to catalog, discover, and discuss their favorite series, chapters, and episodes.

## User Personas

1. **Regular User**: Browses catalog, reads chapters, interacts in forums/groups, manages their reading list.
2. **Admin/Staff**: Manages content (uploading chapters, editing manga data), moderates user forums and groups.
3. **Guest**: Can browse the public catalog but needs to register to interact or read specific content.

## Core Constraints

- **Stack**: Django (Python) backend, SQLite/PostgreSQL database, HTML/CSS/Vanilla JS frontend.
- **Performance**: Must efficiently handle large files for chapter image uploads.
- **Responsive Design**: The UI must be mobile-friendly and scale well from desktop to mobile.

## Tech Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python 3.x, Django
- **Database**: SQLite (local), PostgreSQL (production/Neon)
- **Testing**: pytest
- **Other**: Django ORM, Git

*(Refer to `RULES.md` for strict agent instructions regarding workflow, boundaries, and code style.)*
