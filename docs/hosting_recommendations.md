# Hosting Recommendations for High-Scale Manga App (>100GB Storage)

**Goal**: Host a Django App + PostgreSQL Database + Object Storage (>100GB) for under **€20 / $25 per month**.

---

## **Option 1: The "Smart Cloud" (Hybrid)**

**Best for**: Scalability, Low Maintenance, "Set and Forget".
**Architecture**: Separate the heavy lifting (Storage) from the App.

* **App Hosting**: **Render (Free -> Starter)**
  * **Cost**: **$0** (Free Tier) or **$7/mo** (Starter, no sleep).
  * **Notes**: Free tier sleeps after 15 mins. Use a ping service (UptimeRobot) to keep awake if free.
* **Database**: **Neon.tech** (PostgreSQL)
  * **Cost**: **$0** (Free Tier: 0.5GB Storage).
  * **Notes**: Text/User data is tiny compared to images. 0.5GB holds ~500k comments/users.
* **Storage (Images)**: **Cloudflare R2**
  * **Cost**: **$1.50/mo** for 100GB ($0.015/GB).
  * **Bandwidth**: **$0 (Free Egress!)**. AWS/Cloudinary charge heavily here.
  * **Total Monthly**: **~$8.50 (with Starter App)** or **~$1.50 (with Free App)**.

**Pros**:

* Infinite scalability (R2 is S3-compatible).
* Zero server maintenance.
* Uses a CDN automatically for fast image loading.

**Cons**:

* Requires integrating `django-storages[s3]`.

---

## **Option 2: The "Powerhouse VPS" (Self-Hosted)**

**Best for**: Maximum Specs per Euro, Full Control.
**Architecture**: Running everything on one big virtual server.

* **Provider**: **Contabo (Cloud VPS S)**
  * **Specs**: 4 vCPU, 8GB RAM, **200GB NVMe SSD**.
  * **Cost**: **€5.50 / month**.
* **Database**: Local PostgreSQL on the VPS (Included).
* **Storage (Images)**: Local Filesystem (200GB Included).
* **Total Monthly**: **€5.50**.

**Pros**:

* Insanely cheap for the performance.
* Massive included storage (200GB is huge).
* Fixed monthly price.

**Cons**:

* **High Maintenance**: You manage security, updates, backups, Nginx, Gunicorn.
* **Single Point of Failure**: If the VPS dies, everything dies.
* **Backup Complexity**: You must manually backup that 200GB of data.

---

## **Option 3: The "European Ecosystem" (Scaleway / Hetzner)**

**Best for**: Data Privacy (GDPR), Managed Services on a Budget.
**Architecture**: Managed AppRunner or VPS with Volume.

* **App Hosting**: **Scaleway (Stardust)** or **Hetzner (CPX11)**
  * **Cost**: **~€3 - €5 / month**.
* **Storage (Images)**: **Scaleway Object Storage** (S3 Compatible)
  * **Cost**: **free up to 75GB**, then €0.013/GB.
  * **Bandwidth**: Free (internal) or very cheap.
* **Database**: Managed PostgreSQL (db-dev-s)
  * **Cost**: **~€10 / month**.
  * *(Or run local DB on VPS to save €10)*.
* **Total Monthly**: **~€15** (fully managed) or **~€5** (self-managed DB).

**Pros**:

* EU-based datacenters (Low latency + Privacy).
* Modular (add volume if space runs out).

---

## **Recommendation**

1. **For Now (Simplest)**: Stick with **Option 1 (Render + Cloudflare R2)**. It requires the least setup change (just swapping Cloudinary for R2 later) and keeps costs effectively zero/low until you scale massively.
2. **For Pure Value (Cheapest)**: **Option 2 (Contabo)** is unbeatable (200GB SSD for €5), but be prepared to learn Linux system administration (Security, Firewalls, Docker).
