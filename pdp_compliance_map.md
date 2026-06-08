# PDP & ISO 27001 Compliance Map 🗺️

This document maps how the technical challenges in **PDP Koans (Django Edition)** directly align with the legal compliance requirements of **Indonesian Personal Data Protection Law (UU PDP)** and **ISO 27001 security controls**.

---

## 📋 Compliance Coverage Table

| Koan Challenge | Legal Aspect (UU PDP) | Standard Control (ISO 27001) | Technical Implementation Topic |
| :--- | :--- | :--- | :--- |
| **Koan 01: Data Minimisation**<br>`koans/k01_data_minimization/` | **Article 16 UU PDP**:<br>Limits of data processing | **Control A.8.11**:<br>Data masking & access restriction | **Data Minimisation & Masking**:<br>Removing irrelevant database fields to reduce exposure risks, and implementing a property method to mask sensitive data (e.g. phone numbers) before logging or rendering. |
| **Koan 02: Explicit Consent**<br>`koans/k02_explicit_consent/` | **Articles 20 & 21 UU PDP**:<br>Written/recorded consent requirement | **Control A.5.15**:<br>Access control & consent management | **Processing Foundations & Proof of Consent**:<br>Validating user consent prior to data processing, and recording audit logs (Consent Logs) with IP address, timestamp, and policy version to prove compliance under Article 21. |
| **Koan 03: Data Security**<br>`koans/k03_data_security/` | **Article 39 UU PDP**:<br>Duty of data security preservation | **Control A.8.24**:<br>Use of cryptography (Encryption *at-rest*) | **Data Security & Cryptography**:<br>Translating ISO 27001 cryptography controls into code by building a custom *EncryptedCharField* using AES (Fernet) to transparently encrypt sensitive data (NIK) at-rest in PostgreSQL. |
| **Koan 04: RBAC & Access Audit Trail**<br>`koans/k04_rbac_audit/` | **Article 40 UU PDP**:<br>Restricted access control rules | **Control A.8.2 / A.5.15**:<br>Access rights & audit logging | **Role-Based Access Control & Audit Trails**:<br>Restricting access to DPO roles using a custom permission class, and automatically logging access details (operator email, customer ID, IP address) for audit compliance. |
