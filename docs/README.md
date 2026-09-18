# EIS — Documentation Index

The complete research + specification for the **European Impact Sprints** platform.
Worked example: **Portuguese citizens → Germany**. Hosted model: Portugal-hosted, origin fixed.

> This folder is the **research**. For the running system — architecture diagrams, what's built
> vs mocked, how to launch it — start at [`../readme.md`](../readme.md).

## Start here
- **`01-plan/IMPLEMENTATION-PLAN.md`** — the master build plan (site map, pages, flows, doc map).

## Folder map

| Folder | Contents |
|---|---|
| `01-plan/` | Master implementation plan (hand this to the build agent) |
| `02-spec/` | Product spec + concept + EUDI wallet research |
| `03-cases/` | The 7 subcategories + per-case docs |
| `04-research/` | Personas, worked cases, documents index, 27-country matrix |
| `05-resources/` | Sources, PDF URLs, assisting platforms |
| `06-subjects/` | Research for the 7 non-residence subjects (Work, Studies, Tax, Health, Social security, Vehicle, Family) |
| `07-emergency/` | What the emergency-alert demo actually implements (API + data model) |
| `assets/pdf/` | Fetched forms (3 PDFs) |

## Files

### 01-plan
- `IMPLEMENTATION-PLAN.md` — full site spec + flows + document reference index

### 02-spec
- `PLATFORM-SPEC.md` — master spec (web + mobile + EUDI + emergency, data model, research plan)
- `PLATFORM-CONCEPT.md` — early concept (superseded by PLATFORM-SPEC)
- `EUDI-WALLET.md` — eIDAS 2.0 / EUDI Wallet timeline + use cases

### 03-cases
- `SUBCATEGORIES.md` — the 7 cases (T1 + M1–M6) that need different procedures
- `cases/travel-short-stay.md` — T1
- `cases/move-work.md` — M1 (employed)
- `cases/move-self-employed.md` — M2 (freelancer/business)
- `cases/move-studies.md` — M3 (student)
- `cases/move-jobseeking.md` — M4 (job seeker)
- `cases/move-economically-inactive.md` — M5 (retiree/remote/means)
- `cases/move-family.md` — M6 (family member)

### 04-research
- `PERSONAS.md` — Tiago (travel) + Beatriz (move)
- `TRAVELING-CASE.md` — PT→DE <3 months
- `MOVING-CASE.md` — PT→DE >3 months (Anmeldung chain)
- `DOCUMENTS-INDEX.md` — master tables (documents, info, rules, authorities)
- `COUNTRY-MATRIX.md` — 27-country registration matrix + 4 clock archetypes
- `SPAIN-VALIDATION.md` — 3rd-country validation (three-clock contrast)

### 05-resources
- `SOURCES.md` — verified primary + secondary sources
- `PDF-URLS.md` — PDF links + fetch notes
- `ASSISTING-PLATFORMS.md` — existing platforms + competitors (MoveToEU etc.)

### 06-subjects
- `README.md` — index + content-model note for the 7 subject files below
- `work.md`, `studies.md`, `tax.md`, `health.md`, `social-security.md`, `vehicle.md`, `family.md` —
  research backing `webapp/data.py`'s `_DE_SUBJECTS` (Germany, all live in the web app today)

### 07-emergency
- `EMERGENCY-DEMO.md` — the emergency-alert demo's backend API, data model, and what's mocked vs
  real; see also `12-EMERGENCY-ROUTING-PROPOSAL.md` below for the target multi-country design

### assets/pdf
- `wohnungsgeberbestaetigung_berlin.pdf` — DE landlord confirmation (§19 BMG)
- `aufenthaltsanzeige_5_freizuegigkeitsgesetz.pdf` — DE residence notice (§5 FreizügG/EU)
- `crue_form_porto.pdf` — PT CRUE form (reverse-direction reference)

### Top-level docs
- `12-EMERGENCY-ROUTING-PROPOSAL.md` — emergency routing proposal (sibling-authored; see it for the
  home-country → host-country → citizen messaging design).
