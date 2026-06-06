# PDP Koans (Django Edition) 🛡️

An interactive, Test-Driven Development (TDD) learning platform built in Django. This project is designed to help developers master the technical implementation of **Indonesian Personal Data Protection Law (UU PDP)** and **ISO 27001 security standards** on the backend.

Unlike traditional terminal-based Koans, this platform runs inside a Docker container and exposes a **progress API endpoint** to track your compliance level dynamically.

---

## 🌟 Key Features

* **Real-world Tech Stack**: Django, PostgreSQL, and Docker.
* **ISO 27001 Compliant**: Focuses on cryptography (A.8.24) and data minimisation principles.
* **On-Point Technical Focus**: Pure backend development, no frontend overhead.
* **Progress API Tracker**: Run test cases dynamically via `GET /api/progress/`.

---

## 🚦 Getting Started

### 1. Prerequisites
Ensure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

### 2. Clone and Spin Up the Services
Clone this repository and spin up the Docker containers:

```bash
docker compose up --build
```

The Django development server will start at `http://localhost:8000`.

### 3. Check Initial Progress
Open your browser or run curl to hit the progress API:

```bash
curl http://localhost:8000/api/progress/
```
![Tangkapan Layar Progress](docs/images/6-of-6-passed.png)

**Initial Response:**
You will see that your completion rate is `0.0%` with failing unit tests because the compliance features are not yet implemented!

---

## ⚔️ The Koan Challenges

Your mission is to fix the security and privacy vulnerabilities in the code under the `koans/` directory.

### 🛡️ Koan 1: Data Minimisation (Pasal 16 UU PDP)
* **Goal**: Minimize stored user fields and protect data exposure.
* **Files to Edit**: [koans/k01_data_minimization/models.py](file:///app/koans/k01_data_minimization/models.py)
* **Task**:
  1. Remove/comment-out unnecessary fields (`religion`, `blood_type`, `political_leaning`) that violate the minimisation rule.
  2. Implement the `masked_phone_number` property to safely mask user phone numbers (e.g., `081234567890` becomes `081****7890`).

### 🛡️ Koan 2: Explicit Consent Logging (Pasal 20 & 21 UU PDP)
* **Goal**: Validate and record the user's explicit consent.
* **Files to Edit**: [koans/k02_explicit_consent/views.py](file:///app/koans/k02_explicit_consent/views.py)
* **Task**:
  1. Reject registration requests (return `400 Bad Request`) if `consent_given` is not `True`.
  2. If consent is valid, save the audit log (`ConsentLog` model) containing the user email, IP address, and privacy policy version before returning `201 Created`.

### 🛡️ Koan 3: Data Security & Encryption (Pasal 39 / ISO 27001 Control A.8.24)
* **Goal**: Protect sensitive data (NIK) at rest using database-level encryption.
* **Files to Edit**: [koans/k03_data_security/models.py](file:///app/koans/k03_data_security/models.py)
* **Task**:
  1. Implement a custom Django model field (`EncryptedCharField`) using Python's `cryptography.fernet.Fernet`.
  2. Enforce encryption when saving data to PostgreSQL (`get_prep_value`).
  3. Enforce automatic decryption when retrieving data via the Django ORM (`from_db_value`).

---

## 🏆 Tracking Progress
As you write the correct code, the dynamic test runner will automatically run each test suite on every API request to `/api/progress/`. Watch your score climb from `0.0%` to `100.0%`!

---

## 🎓 UU PDP & ISO 27001 Compliance Map

These Koan challenges are mapped directly to the legal articles of the Indonesian Personal Data Protection Law (UU PDP) and ISO 27001 security standards. You can view the compliance details in your preferred language:

* 🇬🇧 **[English - PDP & ISO 27001 Compliance Map](file:///app/pdp_compliance_map.md)**
* 🇮🇩 **[Bahasa Indonesia - Peta Kepatuhan UU PDP & ISO 27001](file:///app/pdp_compliance_map_id.md)**

