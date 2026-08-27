# Session Summary — What This Agent Did

> ⚠️ **Superseded.** The canonical project summary is now `docs/01-plan/IMPLEMENTATION-PLAN.md` +
> `docs/README.md`. Folder was later renamed `documentation/` → `docs/`. This file is a historical
> session log, kept for reference only.

> Meta-document: a record of the work done in this session, for review.
> Written: 27 Aug 2026. Project: **EIS (European Impact Sprints)**.

---

## 1. The task (as requested)

Build the research foundation for **European Impact Sprints (EIS)** — a unified European mobility
platform. One interface for *traveling to* or *moving into* any EU country, removing the pain of
hunting down information + documents yourself.

Specifically:
- Consider a **traveling case** and a **moving-in case**
- Create **personas**, work through the process step-by-step (what to do, how, what to fill, what to check)
- Leverage **existing assisting platforms**
- Identify **documents needed** and **information needed**
- List **sources** and **PDF URLs** (fetch forms where possible)

**Worked example** (clarified mid-session): **Portuguese citizens → Germany**.

---

## 2. What was delivered

All research lives in `EIS/documentation/` (the shared folder, per the user's convention):

| File | Content |
|---|---|
| `00-PLATFORM-CONCEPT.md` | Product vision, user flow (dashboard → country → travel/move → subject → tabs), EUDI + emergency |
| `01-PERSONAS.md` | Tiago (travel 3wk) + Beatriz (move to Berlin), both Portuguese |
| `02-TRAVELING-CASE.md` | PT→DE <3 months, step-by-step |
| `03-MOVING-CASE.md` | PT→DE >3 months, step-by-step (Anmeldung chain) |
| `04-DOCUMENTS-INDEX.md` | Master tables: documents, info fields, rules, authority map, DE/PT/ES contrast |
| `05-SOURCES.md` | Verified primary + secondary sources |
| `06-PDF-URLS.md` | Direct PDF links + fetch notes |
| `07-ASSISTING-PLATFORMS.md` | Existing EU/DE/PT platforms |
| `08-EUDI-WALLET.md` | eIDAS 2.0 / EUDI Wallet research |
| `assets/pdf/` | 2 fetched forms (see §7) |

> `09-FULL-PLATFORM-SPEC.md`, `10-SPAIN-VALIDATION.md`, `11-COUNTRY-MATRIX.md` were written by a
> **sibling agent** working in parallel — this agent preserved and folded them in, but did not
> author them.

---

## 3. Key research findings (verified, primary sources)

### Traveling (< 3 months) — no formalities
- EU citizens need **only a valid ID/passport**. No visa, no residence permit, no registration.
- EHIC covers temporary state healthcare.

### Moving (> 3 months) — the Anmeldung chain
Germany (unlike Portugal) registers **immediately on move-in**:

1. **Housing** → signed rental contract → **Wohnungsgeberbestätigung** (landlord confirmation).
2. **Anmeldung** at the Bürgeramt within **14 days** of moving in — fine up to **€1,000**.
3. **Meldebescheinigung** (registration cert) + automatic **Steuer-ID** (tax ID) by post.
4. **Health insurance** — mandatory.
5. **Social security number** (Rentenversicherungsnummer) via employer/insurer.
6. **Bank account** (after Anmeldung).
7. No residence permit needed (freedom of movement).

**Key trap documented:** the lease alone is NOT enough — the landlord confirmation (§19 BMG) is
required separately.

### Deadline clocks differ per country (the platform's core logic)

| | Germany | Portugal | Spain |
|---|---|---|---|
| Registration timing | **14 days** from move-in | **30 days after month 3** | **within 3 months** of entry |
| Fine | up to €1,000 | €400–1,500 | none specified |
| Authority | Bürgeramt | Câmara Municipal | Oficina de Extranjería |
| Landlord form | ✅ required | address proof | none (padrón) |
| Tax ID | Steuer-ID (auto) | NIF (apply) | NIE (assigned) |

### EUDI Wallet (eIDAS 2.0)
- Regulation (EU) 2024/1183. Member states must offer **≥1 wallet by 24 Dec 2026**.
- Regulated entities must accept it ~Dec 2027.
- Confirms the user's "wallet in ~half a year" — matches Dec 2026.

---

## 4. Personas

| | Tiago (travel) | Beatriz (move) |
|---|---|---|
| Origin → dest | PT (Lisbon) → DE (Berlin) | PT (Porto) → DE (Berlin) |
| Duration | 3 weeks | indefinite |
| Registration | none | Anmeldung (14d) |
| Tax ID | no | Steuer-ID (auto) |
| Health | EHIC | mandatory DE insurance |

---

## 5. Documents identified

**Travel:** valid ID (+ EHIC recommended).

**Move (full checklist):**
1. Valid ID/passport
2. Employment contract / self-employment proof
3. Wohnungsgeberbestätigung (landlord confirmation)
4. Anmeldung → Meldebescheinigung (Bürgeramt)
5. Steuer-ID (auto, BZSt)
6. Health insurance membership
7. Rentenversicherungsnummer (social security)
8. Bank account (IBAN)

---

## 6. Assisting platforms (leveraged/mirrored)

- **EU:** Your Europe, EURES, SOLVIT, e-Justice, EHIC portal
- **Germany:** Make it in Germany, EU Gleichbehandlungsstelle, Auswärtiges Amt, service.berlin.de,
  Deutsche Rentenversicherung, BZSt
- **Portugal (origin):** gov.pt, ePortugal, AIMA, Portal das Finanças, Segurança Social

---

## 7. PDFs fetched (real files, text-extracted)

| File | What |
|---|---|
| `assets/pdf/wohnungsgeberbestaetigung_berlin.pdf` | DE landlord-confirmation form (§19(3) BMG), 1p |
| `assets/pdf/crue_form_porto.pdf` | PT CRUE form + guide (2pp) — reverse-direction reference |

Source URLs are in `06-PDF-URLS.md`. No fabricated URLs — all links verified against page content
or search results.

---

## 8. Corrections made during the session

1. **Destination country** — original example "Portugal → Lisbon" was ambiguous (Lisbon *is* in
   Portugal). User clarified: **Portuguese citizens → Germany**. All destination-side docs rewritten
   from PT to DE.
2. **Folder naming** — user asked documentation NOT live in a `docs/` folder; moved everything to
   `EIS/documentation/` (the shared folder other agents also use).
3. **Project reconciliation** — user confirmed `EIS/` is the code; research was folded into it.

---

## 9. Open items (not done — flags for the user)

- **Git state** — a sibling agent committed `docs/` to branch `dev-erik` (commits `0a747df`,
  `20b5f34`). This agent's rename to `documentation/` is **unstaged** (shows as delete+add).
  Decision needed: who stages/commits the rename, and whether the sibling should switch to
  `documentation/` too.
- **Memory/skill registration** — not yet saved (offered, awaiting go-ahead).
- **Next research** — per `09-FULL-PLATFORM-SPEC.md` §10: build the 27-country matrix, track
  wallet rollout, spec the MVP.
