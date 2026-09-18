# 12 — Subcategories (the cases that need different procedures)

> **Question this answers:** "traveling vs moving" is too coarse. What are the *actual* cases,
> each needing different procedures, documents, and deadlines?
>
> **Answer:** the cases are defined by EU law — **Directive 2004/38/EC** (freedom of movement),
> mirrored in Germany's **Freizügigkeitsgesetz/EU**. Each Article creates a *different* set of
> conditions → different procedures.

---

## 1. The two top-level intents

| Intent | Legal basis | What changes |
|---|---|---|
| **Traveling** (short stay <3 months) | Art. 6(1) 2004/38/EC | Nothing. Valid ID only. No registration, no conditions. |
| **Moving** (long stay >3 months) | Art. 7(1) 2004/38/EC | Registration + a condition you must satisfy. |

The key insight: **traveling has no subcategories that matter** (a tourist, a business traveler,
and a short-term remote worker all do exactly the same thing — nothing). **Moving splits into
subcategories** because Art. 7(1) has *four different conditions*, each with its own paperwork.

---

## 2. The subcategories (7 cases total)

### A. Traveling — 1 case

| # | Case | Definition |
|---|---|---|
| **T1** | **Short stay / visiting** | Any purpose under 3 months: tourism, business, remote work, visiting family. |

### B. Moving — 6 cases (one per Art. 7(1) condition, + job-seeking)

| # | Case | Legal basis | Definition |
|---|---|---|---|
| **M1** | **Work — employed** | Art. 7(1)(a) | Hired by a German employer. |
| **M2** | **Work — self-employed / freelance / business** | Art. 7(1)(a) | Freelancer, trader, or own business. |
| **M3** | **Studies** | Art. 7(1)(c) | Enrolled in a recognized German institution. |
| **M4** | **Job-seeking** | Art. 14(4)(b) | Looking for work (special ~6-month window). |
| **M5** | **Economically inactive** | Art. 7(1)(b) | Sufficient resources + insurance — retiree, remote worker, digital nomad, independent means. |
| **M6** | **Family member** | Art. 7(1)(d) | Joining / accompanying an EU citizen (spouse, child, dependent parent). |

---

## 3. Why these are the cases (and not more)

The four Art. 7(1) conditions are the *complete* legal basis for >3-month residence. Every real
scenario maps to exactly one:

| Real scenario | Case |
|---|---|
| "I got a job at a Berlin startup" | M1 (worker) |
| "I'm a freelance designer moving my business" | M2 (self-employed) |
| "I'm doing a master's at TU Berlin" | M3 (studies) |
| "I'm moving to find a job" | M4 (job-seeking) |
| "I'm retired / I work remotely for a PT company" | M5 (economically inactive) |
| "I'm joining my spouse who works there" | M6 (family member) |

Note: **remote worker / digital nomad** (working for a non-German employer) is **NOT** M1 (worker)
— that requires a *German* employer. It's M5 (economically inactive) because their income comes
from outside Germany. This is a common and important distinction.

---

## 4. What actually differs per case (the comparison matrix)

All M-cases share a **baseline**: Anmeldung (14 days, €1,000 fine), Wohnungsgeberbestätigung,
Steuer-ID (auto), bank account. The table shows the **delta**:

| | M1 Worker | M2 Self-employed | M3 Student | M4 Job-seeker | M5 Inactive | M6 Family |
|---|---|---|---|---|---|---|
| Key proof | employment contract | business/trade registration | enrolment + resources | job-search proof | resources + insurance | relationship proof |
| Health insurance | via employer | self-arranged | student (discounted) | self-arranged | comprehensive | via main citizen |
| Social security | via employer | self-register (optional) | usually exempt | no | no | as main citizen |
| Extra registration | — | Finanzamt + Gewerbe | university | Agentur für Arbeit | — | — |
| Deadline beyond Anmeldung | start work | before trading | before enrolment | 6-month window | none | none |
| Residence permit | none | none | none | none | none | none (EU family) |

---

## 5. The complete document/info index per case

Detailed per-case docs live in [`cases/`](./cases/) — one per case:

| Case | Doc |
|---|---|
| T1 Short stay / visiting | `cases/travel-short-stay.md` |
| M1 Work — employed | `cases/move-work.md` |
| M2 Self-employed | `cases/move-self-employed.md` |
| M3 Studies | `cases/move-studies.md` |
| M4 Job-seeking | `cases/move-jobseeking.md` |
| M5 Economically inactive | `cases/move-economically-inactive.md` |
| M6 Family member | `cases/move-family.md` |

Each case doc follows one template:
1. **Who this is** (+ legal basis)
2. **Information we provide** (website content)
3. **Procedures** (step-by-step)
4. **Deadlines**
5. **Documents** (with URLs)
6. **Sources**

---

## 6. Legal basis (primary source)

- **Directive 2004/38/EC** — free movement of EU citizens and family members:
  - Art. 6(1) — right of residence ≤3 months (no conditions, ID only).
  - Art. 7(1)(a) — workers + self-employed.
  - Art. 7(1)(b) — sufficient resources + comprehensive health insurance.
  - Art. 7(1)(c) — students (+ resources + insurance).
  - Art. 7(1)(d) — family members.
  - Art. 14(4)(b) — job-seekers (can't be expelled while genuinely seeking work).
  - Art. 16 — permanent residence after 5 years.
- **Freizügigkeitsgesetz/EU (Germany)** — implements the directive; §2 conditions, §5 notice of
  residence (Aufenthaltsanzeige form — see `../assets/pdf/`).
