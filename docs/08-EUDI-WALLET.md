# 08 — EUDI Wallet (European Digital Identity Wallet)

The digital identity layer our travel-notification + emergency system will build on.

## What it is
The **European Digital Identity Wallet** (EUDI Wallet) is a personal digital wallet that lets EU
citizens prove their identity and share verified attributes (name, age, address, nationality,
qualifications) across borders — to both public and private services. Governed by the revised
**eIDAS Regulation — Regulation (EU) 2024/1183**.

## Timeline (verified)
| Milestone | Date |
|---|---|
| Regulation (EU) 2024/1183 in force | 2024 |
| Implementing Regulation (EU) 2026/1731 (wallet setup/interop) | adopted July 2026 |
| **Member States must offer ≥1 EUDI Wallet** | **24 Dec 2026** |
| Regulated entities (banks, telcos, large platforms) must accept it | ~Dec 2027 (1 yr later) |

> User said "digital EU-identified wallet coming up in half a year" — matches the Dec 2026
> mandatory-availability deadline.

## What the wallet carries (relevant attributes)
- Person identification data (name, DoB, nationality)
- Address
- eID / travel document attributes (future: mobile travel document)
- Verified credentials issued by public authorities

## Our two use cases

### 1. Travel notification
Today: no mechanism to tell a destination country "I am coming, for X days, from Y."
With EUDI Wallet: user presents wallet → destination authority receives a **verifiable
notification** of travel intent + duration. This is the foundation of our platform's
"inform the countries" feature.

### 2. Emergency system
In an emergency (medical, disaster), authorities currently rely on physical documents.
With EUDI Wallet: instant, cryptographically-verified identity + origin + next-of-kin data.
This is our planned emergency layer.

## Technical reference
- ARF — Architecture & Reference Framework (EU Digital Identity Wallet technical spec)
  https://ec.europa.eu/digital-building-blocks/sites/spaces/EUDIGITALIDENTITYWALLET/
- Implementing Act on wallet interoperability: Implementing Regulation (EU) 2026/1731

## Open questions for the platform (to resolve later)
- Which wallet attributes are exposed per country (harmonization still in progress).
- How to trigger a "travel notification" — is there a standard flow, or do we define one?
- Emergency access: how authorities request data (consent / legal basis) — GDPR-sensitive.
- Non-EU citizens: wallet availability differs (we target EU citizens first).

## Sources
- EC Digital Building Blocks — European Digital Identity Regulation page (URL in 05-SOURCES.md)
- Gataca timeline — https://www.gataca.io/resources/blog/eIDAS2-timeline/
- Namirial status check — https://www.namirial.com/en/blog/stories/status-check-eudi-wallet/
- Regulation (EU) 2024/1183 (eIDAS 2.0)
