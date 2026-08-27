# EIS — Website Implementation Plan (Master)

> **Purpose:** the single source of truth for the AI agent(s) implementing the EIS web platform.
> Describes every page, component, flow, and the exact document that feeds it. Read this first.
>
> **Hosting model:** Portugal-hosted instance. **Origin fixed = Portugal (Portuguese citizens).**
> **Destination = Germany** (primary worked case; 27-country data available for expansion).
>
> **Current state:** `../../webapp/` is a Streamlit prototype (single dashboard, Residence-only
> subject, wallet stubs disabled). **This plan specs the target** — a multi-page, professional
> EU-portal look (no Streamlit-default / "AI-ish" chrome). The Flask EUDI verifier is `../../login_app.py`.

---

## 1. Site map

```
/                          Home / landing (hero, disclaimer, country picker, intent cards)
/moving/<subcategory>      Subcategory page (personalized; widgets; documents; Inform-with-ID)
/traveling                 Traveling page (light: info + deadlines + Inform-with-ID)
/inform                    "Inform with ID" — EUDI Wallet travel notification flow
/document/<id>             Document detail (PDF viewer + Sign)
```

---

## 2. Design system (professional EU portal — no "AI-ish" look)

Reference the **EU official portals** for look & feel (see `../05-resources/ASSISTING-PLATFORMS.md`):
- **Your Europe** (europa.eu/youreurope) — the closest design reference: clean, blue/neutral,
  official, accessible.
- **Make it in Germany** (make-it-in-germany.com) — national-portal pattern.
- Competitor to beat: **MoveToEU** (movetoeu.eu) — strongest direct competitor; study its
  country-guide structure, then do it cleaner and EU-official-looking.

**Non-negotiables:**
- Neutral official palette (EU blue `#0E47CB` accent + white/grey), no gradients, no emoji-hero,
  no AI-generated stock imagery in the hero.
- Real typographic hierarchy, generous whitespace, clear labels (not "vibe" placeholder copy).
- Accessibility (WCAG AA): sufficient contrast, keyboard nav, semantic HTML.
- Every fact on screen traces to a source in `../05-resources/SOURCES.md` — no invented data
  (the `../04-research/COUNTRY-MATRIX.md` explicitly marks `UNVERIFIED` items; render those as
  "penalties may apply" or badge them, never invent a number).

---

## 3. Page 1 — Home / landing (`/`)

### 3.1 Hero section
- Headline: e.g. **"Moving within Europe, made simple."** + one-line subhead ("One place for the
  documents, deadlines and rules of your EU move — tailored to Portuguese citizens.").
- A single clear primary CTA scrolls to the intent picker below. No clutter.

### 3.2 Disclaimer (above the intent cards)
A short banner between hero and the intent selection. Proposed copy (threshold = the EU-wide
**3-month / 90-day** rule, Directive 2004/38/EC Art. 6 vs 7):

> "**How long will you stay?** Under 3 months → **Traveling** (no registration needed, just a valid
> ID). Over 3 months → **Moving** (you must register your residence)."

**Edge-case note (researched):** the 3-month line is the EU baseline, but some countries trigger
registration **on move-in** (Germany 14 days, `../04-research/COUNTRY-MATRIX.md` archetype 1)
rather than at the 3-month mark. If the user picks "Moving" the subcategory pages surface the
**correct per-country clock** — this is the core value, never a one-size warning.

### 3.3 Country picker
- Dropdown of **27 EU member states** (+ EEA/CH later). Selection is **recorded** (state/URL
  param/localStorage) and drives all downstream content.
- Origin is fixed to Portugal (hosted model) — show it as a static badge ("Portuguese citizen?").

### 3.4 Intent selection — two large cards

- **Traveling** → a **single button/card** (no subcategories — confirmed: a tourist, business
  traveler and short remote worker all do the same thing, `../03-cases/cases/travel-short-stay.md`).
  → routes to `/traveling`.
- **Moving** → a card that **expands into subcategories** (dropdown or icon menu):
  `../03-cases/SUBCATEGORIES.md` §2:
  1. Work — employed → `/moving/work`
  2. Work — self-employed / freelance / business → `/moving/self-employed`
  3. Studies → `/moving/studies`
  4. Job-seeking → `/moving/jobseeking`
  5. Economically inactive (retiree / remote / digital nomad) → `/moving/economically-inactive`
  6. Family member → `/moving/family`
  Each routes to its subcategory page.

---

## 4. Page 2 — Moving subcategory page (`/moving/<case>`)

Content source: the matching `../03-cases/cases/<case>.md` (each already contains info,
procedures, deadlines, documents, sources).

### 4.1 Top bar — "Inform with ID"
- Text block: "**Inform your country you're going.** Tell Portugal (and Germany) you are traveling,
  so you can be reached in an emergency." + a primary button **"Inform with ID"**.
- Button routes to `/inform` (EUDI Wallet flow, §6).

### 4.2 Widget categories (below Inform-with-ID)
Each is an expandable widget/section:

| Widget | Content | Doc source |
|---|---|---|
| **Deadlines** | the compliance clock: what, when, fine | `cases/<case>.md` §3 |
| **Necessary documents** | the checklist of documents | `cases/<case>.md` §4 + `../04-research/DOCUMENTS-INDEX.md` |
| **Information needed** | the fields/rules to know | `cases/<case>.md` §1 + `../04-research/DOCUMENTS-INDEX.md` §B |
| **Documents** | pressable cards, one per document | §4.3 below |

### 4.3 Document widget (expandable, pressable)
Each document is a card that expands to show its **metadata block** (all fields already defined
in `../02-spec/PLATFORM-SPEC.md` §4.3):

- **Initial information** — what it is, purpose, legal basis.
- **Information shared** — which personal data is disclosed.
- **To whom** — receiving authority.
- **How long** — default retention, and whether the user can shorten it.
- **Reissuable?** — can it be re-issued.
- **Where submitted** — office/portal/appointment.

The card links to `/document/<id>` (PDF viewer + Sign).

### 4.4 Document detail + signing flow (`/document/<id>`)

1. **Read:** fetch the PDF from its URL (`../05-resources/PDF-URLS.md`; assets in `../assets/pdf/`)
   and render it in an embedded viewer.
2. **Sign:** a "Sign with EU Digital Identity Wallet" button (EUDI, see `../02-spec/EUDI-WALLET.md`).
3. **Confirm:** on sign, a confirmation screen lists **exactly what will be disclosed** and
   **what is still missing** (fields the wallet doesn't have).
4. **Auto-fill:** the document's fields are pre-filled from the wallet's verified attributes
   (name, nationality, address, …).
5. **Generate:** on confirm, an **auto-generated PDF** with the fields filled is produced.
6. **Download:** the user downloads the filled PDF.
7. **Submit:** the page shows the submission procedure (where/how to send — office, portal,
   appointment), sourced from `cases/<case>.md` §2 + §4.

> ⚠️ Wallet is **not yet production-live** (mandatory from 24 Dec 2026, `../02-spec/EUDI-WALLET.md`).
> Build the Sign button + flow behind an interface now; it activates when production wallets roll
> out. The Flask verifier `../../login_app.py` is the prototype (OpenID4VP, mocked verification).

---

## 5. Page 3 — Traveling page (`/traveling`)

Content source: `../03-cases/cases/travel-short-stay.md`.

- Lighter than a moving page — **no document checklist** (a short stay needs only a valid ID).
- Still shows: **Information needed** (stay length, health coverage, purpose) + **Deadlines**
  (the 3-month boundary, 183-day tax note) — see `cases/travel-short-stay.md` §1/§3.
- Includes the **"Inform with ID"** button (emergency reach still applies to travelers).
- Note: some destinations *could* still need documents even for short stays (rare) — keep the
  Documents widget **conditional per country** (data-driven, not hard-coded off).

---

## 6. "Inform with ID" flow (`/inform`) — EUDI Wallet travel notification

Flow source: `../02-spec/PLATFORM-SPEC.md` §4.4 + `../02-spec/EUDI-WALLET.md`.

1. **Why page** — "what is it / why notify / how it helps in an emergency" (so the destination +
   origin countries can reach you in a crisis).
2. **Duration selection** — user picks travel dates (length of stay) + retention length
   (how long the notification is kept, with a stated default the user can shorten).
3. **Confirmation** — summary of exactly what's shared and for how long.
4. **Sign** — user signs with the EUDI Wallet (cryptographic consent).
5. **Backend notifies** the origin (Portugal) + destination (Germany) authorities.
6. **Inform page** — success state, then return.
7. **Erasure** — data deleted after the retention period.

**Open legal/research items** (do not fake a solution — see `../02-spec/PLATFORM-SPEC.md` §9):
- No standard "notify travel" EUDI flow exists yet → we define it (or integrate with Art. 110
  EECC public-warning + consular channels).
- Intra-EU legal basis for home-country → host-country targeted messaging needs research.

---

## 7. Data model

Extends `../02-spec/PLATFORM-SPEC.md` §8. Key entities the UI consumes:
`country` · `intent` · `case` (the 7 subcategories) · `step` · `document` (with the §4.3 metadata
fields) · `deadline` · `info` · `travel_notification` · `signed_document`.

---

## 8. Document reference index (every doc + what it feeds)

| Doc | Feeds |
|---|---|
| `../02-spec/PLATFORM-SPEC.md` | Master spec (pages, data model, §4.3 metadata, flows) |
| `../02-spec/PLATFORM-CONCEPT.md` | Early concept (superseded by PLATFORM-SPEC for build) |
| `../02-spec/EUDI-WALLET.md` | Inform-with-ID + Sign buttons, wallet timeline |
| `../03-cases/SUBCATEGORIES.md` | Home-page Moving subcategory menu (the 7 cases) |
| `../03-cases/cases/*.md` (7) | Each Moving subcategory page + Traveling page |
| `../04-research/DOCUMENTS-INDEX.md` | Documents/Information widgets (master tables) |
| `../04-research/PERSONAS.md` | Test users (Tiago travel, Beatriz move) |
| `../04-research/TRAVELING-CASE.md` | Traveling page content |
| `../04-research/MOVING-CASE.md` | Germany moving baseline (Anmeldung chain) |
| `../04-research/COUNTRY-MATRIX.md` | 27-country dataset + clock archetypes (seed data) |
| `../04-research/SPAIN-VALIDATION.md` | 3-country clock contrast (QA the generalisation) |
| `../05-resources/SOURCES.md` | Source attribution for every fact on screen |
| `../05-resources/PDF-URLS.md` | PDF fetch URLs for the document viewer |
| `../05-resources/ASSISTING-PLATFORMS.md` | Design references + competitors (incl. MoveToEU) |
| `../assets/pdf/*.pdf` (3) | Actual forms (DE landlord conf., DE §5 notice, PT CRUE) |

---

## 9. Build order (recommended)

1. Multi-page skeleton (routes above) + design system (EU-portal look).
2. Home page (hero, disclaimer, country picker, intent cards with Moving subcategories).
3. Germany Moving subcategory pages (M1–M6) from `cases/*.md`.
4. Traveling page.
5. Document detail page + PDF viewer (Sign button as wallet-gated stub).
6. Inform-with-ID flow (wallet-gated until production wallets live).
7. Expand to other 26 countries from `COUNTRY-MATRIX.md` (badge unverified rows).

---

## 10. Open items for the user

- **Canonical folder: `docs/`** (resolved — everything folded in; `documentation/` removed).
- **Sibling `webapp/README.md` paths** — still references flat `docs/00…`, `docs/09…`; update to
  `docs/02-spec/…` etc. (the sibling is actively editing `webapp/` — coordinate before touching).
- **Wallet-gated features** land ~2027 — confirm MVP ships mobility content first, wallet later.
