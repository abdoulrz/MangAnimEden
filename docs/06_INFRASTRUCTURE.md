# Infrastructure Specification: Contabo VPS Environment

This document outlines the current state and planned upgrades for the MangaAnimEden infrastructure hosted on Contabo VPS. It serves as a living specification (`SPEC`) in accordance with `01_RULES.md`, ensuring all future deployments adhere to these best practices.

## 1. Private Networking (Security & Isolation) 🔒

**Status**: Highly Relevant / Planned for immediate implementation.

### The Problem (`The Exposure Problem`)

Currently, secondary services like PostgreSQL (port `5432`) may be exposed on the public internet interface of the VPS. Even if secured by passwords, public exposure invites brute-force attacks and unnecessary risk.

### The Solution

Implement Contabo's **Private Networking**.

- Assign the PostgreSQL instance to bind **only** to the private IP (`127.0.0.1` locally, or the internal Contabo VPC IP if scaled).
- Applications (Gunicorn/Django) communicate with the database exclusively over this private, non-routable interface.
- If the architecture ever scales horizontally (e.g., separating the DB onto a dedicated node or adding a Redis cache server), all internal traffic routes through the Private Network. This ensures internal traffic remains free, fast, and completely invisible to the public internet.

**Action Item:**

- [ ] Verify `postgresql.conf` is binding `listen_addresses` correctly (e.g., `listen_addresses = 'localhost'` or a specific internal IP, NOT `*`).
- [ ] Ensure `ufw` blocks all incoming traffic on `5432` from public interfaces.

---

## 2. Custom Image Storage (Disaster Recovery & Scaling) 💾

**Status**: Recommended / Next step after production stability.

### The Problem (`The Scaling Problem`)

Setting up a new server manually utilizing the `CONTABO_MIGRATION_GUIDE.md` and `setup_step1.sh` scripts is functional, but slow and prone to human error (e.g., environment differences, updated package versions causing conflicts).

### The Solution

Utilize Contabo's **Custom Image Storage**.

- Once the application is stable and fully configured on the VPS (with Nginx, Gunicorn, PostgreSQL, SSL, Redis, and Celery running smoothly), create a snapshot `.iso` or `.qcow2` of the current environment.
- This creates a perfect baseline. If the server experiences catastrophic failure, or if a cloned staging environment is needed, a new VPS can be provisioned using this Custom Image in minutes.
- It essentially transforms a manual configuration process into an immutable infrastructure deployment.

**Action Item:**

- [ ] Stabilize current deployments (Phase 3.5 -> 5.3 completion).
- [ ] Take a snapshot of the fully operational VPS using the Contabo Cloud Control Panel and save it to Custom Image Storage.

---

## What is NOT Relevant Currently

- **Cloud-init / API / CLI Management**: Overkill for the current single-server, monolithic deployment stage.
- **1-Click Apps**: Unnecessary, as the Django + React(soon) + Nginx custom stack is already manually containerized/deployed.

## TL;DR Directive

Private Networking is the most actionable item required right now for tighter security of the database. Custom Image Storage serves as the ultimate insurance policy and should be executed immediately once the VPS deployment reaches its final, steady state.
