# 09 — Full Platform Specification (Web + Mobile)

> The master specification for the **European Impact Sprints (EIS)** unified mobility platform.
> Consolidates the existing research (`00`–`08`) with the full product vision described by the
> founder, including the **web application**, the **mobile application**, the **EUDI Wallet
> integration**, and the **emergency management system**. Also contains the research findings and
> the **step-by-step research plan** for the features still to be investigated.
>
> Status: **Specification / research phase.** No production code yet. `EIS/app.py` is a prototype
> EUDI verifier (see §6.5), not production-ready.

---

## 1. Executive summary

EIS is a **unified platform for intra-European travel and relocation**. Today an EU citizen moving
between countries must hunt across each destination country's government websites to find the
right documents, deadlines, and procedures — and the rules (registration windows, fines, required
forms) differ per country. EIS replaces that with **one interface**:

1. Pick a **destination country** (27 EU member states).
2. Say whether you are **traveling** (short stay) or **moving** (long stay).
3. Pick a **subject** (work, studies, residence, tax, health, …).
4. Get a structured dashboard of **documents** (with sign + download), **deadlines**, and
   **information** — all tailored to your specific origin→destination case.

On top of this sits an **identity + emergency layer**:

- **"Inform with ID"** — a citizen notifies their destination country (and origin country) that
  they are traveling there, for a chosen period, using the **EU Digital Identity Wallet**
  (eIDAS 2.0). Cryptographically verifiable, privacy-preserving.
- **Document signing** — citizens can sign official forms using the wallet and download the signed
  document.
- **Emergency management (mobile app)** — if an emergency happens in the destination country,
  the origin country can reach its citizens there with targeted **SMS + push notifications**,
  including optional **precise location disclosure** so authorities can give exact instructions.

The platform is **hosted by each country** (a Portugal-hosted instance serves Portuguese citizens
traveling to Germany, etc.), so each state retains sovereignty over its own citizens' data.

---

## 2. Problem statement

| # | Problem | Today's reality |
|---|---|---|
| 1 | **Fragmented information** | Each traveler must search the destination country's websites to find documents, deadlines, and procedures. |
| 2 | **Per-country rules differ** | Germany: Anmeldung within **14 days** of move-in (fine up to €1,000). Portugal: CRUE **30 days after month 3** (fine €400–1,500). One generic guide is wrong for someone. |
| 3 | **No travel notification** | There is no standard mechanism for a citizen to tell a destination country "I am coming, for X days, from Y" — which also means no reliable way to reach them in an emergency. |
| 4 | **Fragmented emergency reach** | In a crisis, authorities rely on physical documents and broadcast warnings; there is no unified, citizen-targeted channel. |
| 5 | **Document friction** | Forms must be found, printed, filled, and submitted manually across different authorities. |

---

## 3. Product vision — one platform, three surfaces

| Surface | Role | Key capability |
|---|---|---|
| **Web app** | Core mobility platform | Country → travel/move → subject → documents/deadlines/info; "Inform with ID"; document signing. |
| **Mobile app** | Emergency + notification layer | Same as web **plus** push notifications, SMS, and location disclosure. |
| **Backend (per-country)** | Orchestration + inter-country comms | Stores notifications, routes emergency messages between states, notifies authorities via APIs. |

The three surfaces share one data model (§8) and one identity layer (§6).

---

## 4. Web application — core mobility platform

### 4.1 Hosting model (per-country)

Each EU member state hosts an instance of the platform **for its own citizens**.

- A **Portuguese** citizen traveling to Germany uses the **Portugal-hosted** instance.
- That instance is configured for **Portugal → {destination}** content: origin fixed, destination
  selectable.
- This keeps each state sovereign over its citizens' data and matches the legal reality that a
  state's duty of care runs toward its own nationals.

### 4.2 User flow (screens)

```
1. Main dashboard
   └─ Country picker: 27 EU member states (scope for now)
        → "Where are you traveling to?"

2. Intent selection (per chosen country)
   ├─ Traveling  (short stay)
   └─ Moving     (long stay / relocation)

3. Subject / subcategory selection (per intent)
   ├─ Work
   ├─ Studies
   ├─ Residence
   ├─ Tax
   ├─ Health
   ├─ Social security
   ├─ Vehicle
   └─ Family

4. Subject dashboard (new page)
   └─ Categories containing all necessary information + documents for that case
        e.g. "Work → bank account", "Residence → registration", etc.

5. Document detail page
   └─ Read the document + see its metadata + Sign button
```

### 4.3 Document model (fields to show per document)

Every document in the platform carries the same metadata, so a user knows exactly what they're
signing up for:

| Field | Meaning |
|---|---|
| **Initial info** | What the document is, its purpose, legal basis. |
| **Information shared** | Which personal data is disclosed / collected. |
| **To whom** | The authority that receives it. |
| **How long** | Default retention period, and whether the user can set their own. |
| **Reissuable?** | Whether the document can be re-issued / re-submitted later. |
| **Where submitted** | The office, portal, or appointment where it is filed. |
| **Read** | Full text / form preview. |
| **Sign** | Trigger the wallet signing flow (§6). |

### 4.4 "Inform with ID" — travel notification via EUDI Wallet

The top of each subject page has a prominent **"Inform with ID"** button. This is the travel
notification feature.

**Purpose:** inform the **destination country** (and origin country) that the citizen is traveling
there for a specific period, so that in an emergency the states can reach them in a unified way.

**Flow when pressed:**

1. **Information page** — explains:
   - *What is it?* — a verifiable travel notification.
   - *Why?* — so the destination + origin countries can assist you in an emergency.
   - *Why do we need this?* — currently there is no standard channel.
   - *How does it benefit you?* — faster, targeted help; proof of presence.
   - *How long is it stored by default?* — stated default retention.
2. **User chooses the period:**
   - **Length of stay** (dates of travel).
   - **Retention length** — how long the notification data is kept after the stay ends (with a
     stated default the user can shorten).
3. **Confirmation** — a summary screen showing exactly what will be shared and for how long.
4. **Sign** — user signs with the **EUDI Wallet** (cryptographic consent).
5. **Backend notifies the countries** — the origin and destination authorities are informed via
   APIs (exact endpoints/standard to be researched — see §9, §10).
6. After the retention period, the data is **erased**.

### 4.5 Document signing flow

1. User selects a document → opens its detail page.
2. Reads it (full preview of the form).
3. Presses **Sign** → same wallet confirmation flow as §4.4 (consent screen → sign).
4. Once signed, the **signed document is downloaded**.

This makes document completion a *digital, signed* transaction instead of print-fill-post.

---

## 5. Mobile application — emergency + notification layer

The mobile app behaves **identically to the web app** for the mobility content, and **adds**:

| Capability | Description |
|---|---|
| **Push notifications** | Real-time alerts to the device. |
| **SMS receive** | Fallback channel when data/push is unavailable. |
| **Location disclosure** | User can opt in to share precise location with authorities during an emergency. |

### 5.1 Emergency communication flow (SMS)

The core scenario the founder described:

1. Citizen **informs the destination country** via "Inform with ID" (§4.4) → the country now knows
   *who* is there, *where*, and *for how long*.
2. An **emergency** occurs in the destination country.
3. Countries **communicate internally** (the destination country alerts the origin country, or the
   origin country learns of the emergency).
4. The **origin country** (citizen's home state) sends a **request** for a custom SMS message to
   the **destination country**.
5. The destination country **forwards** that message to the phone numbers of that country's
   registered citizens.
6. Each citizen receives a **custom SMS** with: what to do, where to go, and how — so they are not
   lost in the crisis.

> **Reality check (verified):** this exact "targeted citizen-of-country-X SMS routed via host
> country" mechanism does **not exist as a standard EU service today.** The building blocks exist
> (§7) but none is nationality-targeted. This is the central **research + design gap** — see §9,
> §10. The platform either *defines* this flow (via the EUDI wallet + a per-country backend) or
> integrates with the existing public-warning + consular channels.

### 5.2 Push notification → detail page

A push notification opens a **detail page inside the app** with the full instructions (not just a
truncated notification). This is the app's advantage over plain SMS.

### 5.3 Location disclosure

- During an emergency, the user can **opt in to disclose their location**.
- This allows the government / destination country to **see precisely where they are**.
- In return the user receives **precise, personalized instructions** (where to go, what to do).
- When resolved, the user is informed the **report is closed**.

### 5.4 Satellite communication

The founder noted satellites are being considered for the emergency channel. Two relevant EU
capabilities exist (see §7.3): **Galileo EWSS** (satellite broadcast of emergency alerts directly
to smartphones) and **IRIS²** (secure satellite connectivity). This is at the **brainstorm stage** —
no decision made. Research + decision required (§10).

---

## 6. EUDI Wallet integration (identity layer)

### 6.1 What it is (verified)

The **European Digital Identity Wallet** (EUDI Wallet) is a personal digital wallet letting EU
citizens prove their identity and share **verified attributes** (name, age, address, nationality,
qualifications) across borders, to public and private services. Governed by the revised **eIDAS
Regulation — Regulation (EU) 2024/1183**.

### 6.2 Timeline (verified)

| Milestone | Date |
|---|---|
| Regulation (EU) 2024/1183 in force | 2024 |
| Implementing Regulation (EU) 2026/1731 (wallet setup/interop) | adopted July 2026 |
| **Member States must offer ≥1 EUDI Wallet** | **24 Dec 2026** |
| Regulated entities (banks, telcos, large platforms) must accept it | ~Dec 2027 |
| **Realistic production wallets in enough hands to verify against** | **late 2026 → 2027** |

> **Implication for MVP:** the wallet is *not yet* broadly available to end users. The platform's
> mobility content (docs/deadlines/info) can ship **before** the wallet is live; the "Inform with
> ID" and document-signing features are **wallet-gated** and will be usable once production
> wallets roll out (late 2026 onward). Build the identity layer behind an interface now, integrate
> for real when wallets are live.

### 6.3 Attributes carried (relevant subset, verified)

- **PID — Person Identification Data** (name, date of birth, nationality, and — per some member
  states — a biometric photograph). PID is issued by the member state and is strong enough for
  KYC/bank-account-grade verification.
- Address.
- eID / travel-document attributes (future: mobile travel document).
- Verified credentials issued by public authorities (QEAA / EAA).

### 6.4 Selective disclosure (verified)

The wallet supports **selective disclosure**: it can prove *"this person is a national of Portugal"*
or *"over 18"* **without revealing the full underlying document**. This is exactly what the
"Inform with ID" flow needs — share only `nationality` + travel dates, nothing else. It also means
the verifier never learns *where else* the citizen used their identity.

### 6.5 Existing prototype — `EIS/app.py`

A minimal Flask **OpenID4VP Relying Party** (verifier) already exists in the repo. It:

- builds an OpenID4VP authorization request (DCQL query) asking for the PID `nationality` claim,
- shows it as a QR code,
- receives the wallet's `vp_token` on `/callback`,
- decodes the SD-JWT and extracts `nationality` against an allow-list.

**Explicitly a prototype, NOT production.** It skips (documented in the file): signature + trust-chain
verification, key-binding checks, revocation/status-list checks, replay protection, and signed
request objects (JAR). A production verifier must implement all of these against the EUDI **ARF**
(Architecture & Reference Framework) and the member-state trust lists. Test against the public
sandbox **eudi-test.dev** (requires an https tunnel, e.g. cloudflared/ngrok).

---

## 7. Emergency & public-warning infrastructure (verified research)

### 7.1 Reverse 112 / EU-Alert — mobile public warning

- **Reverse 112** = authorities warn people in a defined geographic area directly on their phones.
- **EU-Alert** = the EU public-warning system using **cell-broadcast** technology (ETSI standards);
  national authorities can disseminate alerts to mobile phones.
- **Legal basis:** **Article 110 of the European Electronic Communications Code (EECC)** requires
  every member state to have a public-warning system (deadline was **June 2022**). Alerts are
  transmitted via mobile number-based services and/or cell broadcast.
- **What it does NOT do:** target by nationality. It warns *everyone in an area*, not "the
  Portuguese citizens in Berlin." This is the gap EIS fills.

### 7.2 Galileo — emergency warning + search and rescue

- **Galileo EWSS (Emergency Warning Satellite Service)** — *under development* — broadcasts alerts
  **globally, directly to smartphones** (any Galileo-enabled device), **without using terrestrial
  radio networks** (which may fail in disasters). Intended for national civil-protection authorities
  to transmit emergency alerts. This is the satellite channel for *outbound* warnings.
- **Galileo SAR (Search and Rescue)** — free service; relays radio-beacon distress signals via
  **COSPAS-SARSAT MEOSAR** to the nearest rescue centre. This is the channel for a *person in
  distress* to be found.

### 7.3 IRIS² + GOVSATCOM — sovereign satellite connectivity

- **IRIS²** is the EU's sovereign satellite constellation (the third, after Galileo and Copernicus),
  providing **secure and reliable connectivity** for governments, emergency services, and
  businesses. Builds on and extends **GOVSATCOM** (the common marketplace for secure governmental
  communication services).
- **Relevance:** the secure, sovereign channel through which *country-to-country* emergency
  messaging could run — but this is a **policy/sovereignty question**, not a plug-in API. Research
  required (§10).

### 7.4 Consular protection — Directive (EU) 2015/637

- **Directive 2015/637** gives an **unrepresented** EU citizen in a **third country** the right to
  seek consular protection from the embassy/consulate of **any** member state, and obliges states
  to coordinate/cooperate to facilitate it. Financial assistance may be repayable (Art. 14).
- **Legal anchor note:** this directive covers **third countries**, not intra-EU movement. Within
  the EU, freedom of movement applies and there is no "consular protection" in the same sense —
  the relevant intra-EU duty is the destination state's ordinary civil-protection duty. This is an
  important legal boundary the emergency feature must respect (see §9.3).

### 7.5 Traveler-registration precedent (the "Inform with ID" analog)

Voluntary citizen travel-registration systems already exist and prove the model:

| System | Country | What it does |
|---|---|---|
| **MFA eRegister** | Singapore | Voluntary registration of overseas travel/residence; lets MFA contact you in an emergency/crisis. |
| **Ariane** | France | Voluntary registration of trips abroad; enables consular contact in a crisis. |
| **STEP** | United States | Smart Traveler Enrollment Program; alerts + contact in emergencies. |

These are **national, siloed** systems. EIS's "Inform with ID" is the **EU-wide, wallet-verified,
privacy-preserving** generalization — and its differentiator is that it *also* notifies the
destination country, not just the home country.

---

## 8. Consolidated data model

Extends the sketch in `PLATFORM-CONCEPT.md` with the identity + emergency + notification
entities.

```
country(id, code, name)                                  -- 27 EU member states
intent(traveling | moving)

subject(residence | tax | work | health | social_security | vehicle | family | studies)

step(id, country_id, intent, subject, name, due_rule, authority, cost, fine)
document(id, step_id, name, form_url, fields[], issuer,
         initial_info, shared_data, to_whom, retention_default, reissuable, submit_where)
info(id, step_id, content, source_url)
deadline(id, step_id, trigger, action, window, fine)

-- Identity + notification layer (new)
travel_notification(id, user_id, origin_country_id, dest_country_id,
                    stay_start, stay_end, retention_until, status, wallet_attestation)
signed_document(id, document_id, user_id, wallet_signature, downloaded_at)

-- Emergency layer (new)
emergency(id, dest_country_id, severity, area, title, body)
emergency_message(id, emergency_id, origin_country_id, dest_country_id, content, channel[push|sms])
location_disclosure(id, user_id, emergency_id, geolocation, shared_until, status)
```

---

## 9. Open questions (to resolve by research)

1. **Travel-notification standard:** is there an existing/emerging EUDI-wallet flow for "notify
   travel intent + duration," or do we define one? Which attributes, which endpoint?
2. **Inter-country emergency routing:** no standard "origin country → destination country → citizen
   SMS" mechanism exists today. Do we define it (per-country backend + APIs), or integrate with
   Article 110 / cell-broadcast / consular channels?
3. **Intra-EU legal basis:** Directive 2015/637 covers *third countries*. Within the EU, what is
   the legal basis for a home country directing targeted emergency messaging to its citizens in
   another EU state? (GDPR, civil-protection law, mutual assistance.)
4. **GDPR / retention:** legal basis for storing travel notifications, location, and the
   user-chosen retention windows. The "erase after retention" feature must map to GDPR storage
   limitation.
5. **Wallet attribute harmonization:** which attributes each member state exposes, and the
   biometric-photo divergence (e.g. Germany includes it, others may not) — risks fragmentation.
6. **Non-EU citizens:** wallet availability differs; platform targets EU citizens first.
7. **Satellite channel decision:** Galileo EWSS (outbound broadcast) vs IRIS² (secure comms) vs
   terrestrial reverse-112 — which covers the emergency messaging requirement, and when is it live?
8. **Per-country content sourcing:** there is no single public "mobility API" — content must be
   curated per country (Your Europe / Make-it-in-Germany are content sources, not APIs).
9. **Production wallet verifier:** `app.py` is mocked; a certified verifier must implement ARF
   trust-chain, key-binding, status-list, replay protection, signed request objects.

---

## 10. Step-by-step research plan (further features)

Ordered so each step de-risks the next. Verified-data rule applies throughout — no fabricated
facts, no invented forms/URLs/statistics.

### Phase A — Validate & generalize the content model

1. **Validate a 3rd destination country** (e.g. Spain, France, or Italy) with the same
   persona→cases→index→sources method. Confirms the per-country deadline clock is *generalizable*,
   not a DE/PT quirk.
2. **Build the 27-country matrix:** for every EU member state capture the fact matrix (short-stay
   right, long-stay conditions, registration authority, timing, fine, landlord proof, tax ID
   acquisition, social/health, residence permit). This becomes the platform's seed dataset.
3. **Expand subjects:** currently residence/tax/work/health/social/vehicle/family/studies are
   placeholders — research each per country (the moving case is the richest; work + studies
   subcategories per §4.2).

### Phase B — Identity layer

4. **Track EUDI wallet production rollout** (which member states have live wallets, when — late
   2026 → 2027). Determines when "Inform with ID" is real vs demo.
5. **Map wallet attributes → travel notification:** define the exact DCQL query (nationality +
   travel dates + retention choice) and whether a standard "notify travel" flow exists or we define
   one.
6. **Production verifier spike:** upgrade `app.py` to a certified verifier (ARF trust-chain, key
   binding, status-list/revocation, replay protection, signed request object). Sandbox against
   eudi-test.dev first.

### Phase C — Emergency system

7. **Research inter-country emergency routing:** confirm what exists (Article 110 EECC, EU-Alert,
   reverse-112, cell broadcast, consular 2015/637) and define EIS's *new* nationality-targeted
   flow — who initiates, who forwards, via what API.
8. **Legal basis (intra-EU):** research the exact legal basis for targeted citizen messaging in
   another EU state (civil protection, mutual-assistance, GDPR Art. 6 legal bases).
9. **Satellite decision:** Galileo EWSS availability/timeline + IRIS² — determine which (if any)
   covers the requirement, or whether terrestrial channels suffice for MVP.
10. **Location disclosure spec:** exact consent flow, precision, retention, and the "report closed"
    lifecycle — plus GDPR impact (precise geolocation is sensitive data).

### Phase D — Privacy, security & MVP

11. **GDPR DPIA:** data-protection impact assessment for travel notifications + location disclosure.
12. **Per-country hosting architecture:** confirm the per-country instance model (sovereignty,
    data residency, cross-border API design).
13. **Define MVP scope + build order:** mobility content (ship first, no wallet dependency) →
    document signing → "Inform with ID" → emergency SMS/push. Write the MVP spec + UI/UX design.

---

## 11. Sources

**EUDI Wallet / eIDAS**
- Regulation (EU) 2024/1183 (eIDAS 2.0) — the EUDI Wallet legal basis.
- Implementing Regulation (EU) 2026/1731 — wallet setup/interoperability.
- EC Digital Building Blocks — EU Digital Identity Wallet / ARF:
  https://ec.europa.eu/digital-building-blocks/sites/spaces/EUDIGITALIDENTITYWALLET/
- Gataca — eIDAS2 timeline: https://www.gataca.io/resources/blog/eIDAS2-timeline/
- EUDI Dev Wallet sandbox: https://eudi-test.dev

**Emergency / public warning**
- Reverse 1-1-2 — Wikipedia: https://en.wikipedia.org/wiki/Reverse_1-1-2
- EU-Alert — Wikipedia: https://en.wikipedia.org/wiki/EU-Alert
- Article 110 EECC — public-warning systems (Interoperable Europe Portal):
  https://interoperable-europe.ec.europa.eu/collection/rolling-plan-ict-standardisation/emergency-communications-and-public-warning-systems-rp-2026

**Satellite**
- Galileo EWSS — EU Agency for the Space Programme: https://www.euspa.europa.eu/galileo-ewss
- Galileo SAR — European GNSS Service Centre: https://www.gsc-europa.eu/galileo/services
- IRIS² — EU Secure Connectivity: https://defence-industry-space.ec.europa.eu/eu-space/iris2-secure-connectivity_en
- GOVSATCOM — https://eu-space.europa.eu/programmes/secure-connectivity-iris2-and-govsatcom

**Consular / traveler registration**
- Directive (EU) 2015/637 — consular protection for unrepresented citizens in third countries:
  https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=celex:32015L0637
- Singapore MFA eRegister: https://eregister.mfa.gov.sg/ (precedent for voluntary travel registration)

**Mobility content (existing research)**
- See `../05-resources/SOURCES.md` (Portugal → Germany worked case), `../05-resources/ASSISTING-PLATFORMS.md`,
  `EUDI-WALLET.md`.
