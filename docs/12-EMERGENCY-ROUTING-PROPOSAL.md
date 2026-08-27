# 12 — Emergency Routing Proposal (inter-country communication)

**Resolves the #1 flagged gap in `09-FULL-PLATFORM-SPEC.md`:** the "home country → host country →
citizen SMS" routing does **not exist** as a standard EU service today. This document maps the
channels that *do* exist, isolates exactly what's missing, and proposes a concrete architecture +
what we propose to the EU/countries.

---

## 1. The problem (restated)

The founder's vision: a citizen informs their destination country where they are; in an emergency,
their **home country** sends a **custom message** that reaches **exactly its own citizens** in the
destination country (not everyone in the area).

Three things must happen:
1. **Detect** the emergency + produce authoritative guidance (destination country's job).
2. **Route** a message from home country → destination country → citizen.
3. **Reach** the citizen on their phone (push / SMS / satellite).

Leg 2 (country→country targeted routing) and leg 3 (targeted *by nationality* delivery) are the
missing pieces. Everything else already exists.

---

## 2. What already exists (verified channels)

| # | Channel | What it is | What it does / does NOT do |
|---|---|---|---|
| 1 | **ERCC** (Emergency Response Coordination Centre) | The 24/7 hub of the **EU Civil Protection Mechanism (UCPM)**; coordinates disaster assistance + real-time info exchange between member states. | Coordinates **assistance** (firefighting teams, equipment, medical) — not citizen notification. |
| 2 | **CECIS** (Common Emergency Communication & Information System) | The IT system ERCC + member states use to exchange emergency info. | G2G emergency messaging between states — but about *resources/response*, not *individual citizens*. |
| 3 | **eDelivery** (CEF building block) + **AS4** protocol | Open-standard, installable software for **secure G2G/B2G digital data exchange** via AS4 Access Points. Already EU-funded. **e-CODEX** is its e-justice sibling. | The **plumbing** to build any new cross-border message network on. Not citizen-facing. |
| 4 | **Lead State concept** (Council guidelines 2008/C317/06) | A member state volunteers to coordinate + evacuate its nationals (and unrepresented EU citizens) in a **crisis in a third country**; states share info about their citizens present. | The closest operational analog to our idea — but scoped to **third countries**, and manual/diplomatic. |
| 5 | **Consular protection** (Directive 2015/637) | Unrepresented EU citizen in a **third country** may seek help from **any** member state's embassy. | Third countries only; reactive (citizen asks), not proactive push. |
| 6 | **IMI** (Internal Market Information System, Reg. 1024/2012) | Trusted, multilingual G2G channel for cross-border administrative cooperation — 67 procedures / 17 policy areas. | Could host a *new* "traveler notification" procedure, but currently none exists for this. |
| 7 | **Cell broadcast / EU-Alert / LB-SMS** (ETSI TS 102 900) | Destination country pushes an alert to **every phone in a geographic area** (cell broadcast + location-based SMS). | Reaches **everyone in the area** — cannot target "Portuguese citizens in Berlin." This is the gap. |
| 8 | **Galileo EWSS** (Emergency Warning Satellite Service) | Satellite broadcast of alerts **directly to phones**, no terrestrial network needed. Under development. | The resilience fallback when networks are down. |

**Conclusion:** detection (ERCC/CECIS), secure G2G transport (eDelivery/AS4), and area broadcast
(cell broadcast / Galileo EWSS) all exist. The **only** missing piece is **nationality-targeted,
consent-based, cross-border citizen notification** — which is exactly what the EIS platform adds.

---

## 3. The key design insight — data sovereignty

**The citizen's personal data never needs to cross a border.**

This is the elegant resolution to the whole problem:

- The citizen registers **only with their home country** (their identity is already verified by the
  EUDI wallet; they consent via the wallet sign in the "Inform with ID" flow).
- In an emergency, the **destination country publishes an alert** (public guidance — no personal data).
- The **home country's** backend receives that alert, matches it against **its own registry** of
  "my citizens currently in that country," and messages **its own citizens**.

Every actor messages only people it has legal authority over. **No cross-border transfer of
citizen personal data** → a dramatically simpler GDPR story, and it preserves each state's
sovereignty (exactly the founder's per-country hosting model).

The founder's original phrasing ("host country forwards the SMS to the numbers of that country")
becomes: **host country publishes the alert; home country forwards it to its own citizens.** Same
user outcome, cleaner legal + technical design.

---

## 4. Proposed architecture (3 legs, 3 existing channels)

```
EMERGENCY IN GERMANY (destination)
        │
        ▼
┌─────────────────────────────────────────────┐
│ LEG 1 — Detect + publish                     │
│ Germany's civil protection authority detects │
│ the emergency, publishes authoritative        │
│ guidance via:                                 │
│   • cell broadcast / EU-Alert (everyone in    │
│     the area)  [existing — channel #7]        │
│   • ERCC / CECIS (notify other member states) │
│     [existing — channels #1, #2]              │
└─────────────────────────────────────────────┘
        │  (public alert, NO personal data)
        ▼
┌─────────────────────────────────────────────┐
│ LEG 2 — Country → country (secure transport) │
│ Germany's platform node → Portugal's platform │
│ node, over **eDelivery / AS4** (or ERCC/CECIS │
│ for civil-protection events, or a new IMI     │
│ procedure). [existing — channels #1–#3, #6]   │
│ Payload: signed alert + guidance content.     │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│ LEG 3 — Home country → its own citizens      │
│ Portugal's backend matches the alert against  │
│ its **own registry** of Portuguese citizens   │
│ currently in Germany (from "Inform with ID"). │
│ Sends **tailored SMS + push** to exactly      │
│ those citizens (roam-like-at-home = SMS works │
│ cross-border at no extra cost).               │
│ Optional: location disclosure → precise       │
│ instructions; "report closed" when resolved.  │
│ Resilience fallback: Galileo EWSS / IRIS².    │
│ [platform's own channel — the NEW part]       │
└─────────────────────────────────────────────┘
```

**Why this works technically today:** SMS and push from Portugal to a Portuguese phone roaming in
Germany already works (EU "roam like at home" regulation — no cross-border surcharge, same number).
The platform only needs the citizen's phone number, which it already has from registration.

---

## 5. Step-by-step flow (user-facing)

1. **Before travel:** citizen completes "Inform with ID" → home country's registry records:
   identity (wallet-verified), destination country, stay dates, phone number, consent to emergency
   contact.
2. **Emergency occurs** in the destination country.
3. **Destination country** publishes the alert (cell broadcast to everyone in the area + ERCC/CECIS
   to member states + platform nodes via eDelivery/AS4).
4. **Home country's node** receives the signed alert, matches its registry → identifies "N of our
   citizens currently in that country."
5. **Home country messages its citizens** — custom SMS + app push: what happened, what to do, where
   to go.
6. **Location disclosure (opt-in):** the citizen can share precise location → destination
   authorities give precise instructions.
7. **Closure:** when resolved, the citizen receives "report closed."

---

## 6. Legal basis — what we propose to the EU / countries

Three escalating options, cheapest first:

| Option | What it is | Effort | GDPR story |
|---|---|---|---|
| **A. Voluntary bilateral (MVP)** | Two countries (e.g. PT↔DE) adopt the platform's travel-notification registry + alert-routing on their own, using eDelivery/AS4 transport. No new law. | Low | Each state processes its **own citizens'** data — normal national law applies. |
| **B. New IMI procedure** | Register a "traveler emergency notification" procedure in IMI (Reg. 1024/2012 already supports adding policy areas). Gives a pre-built, trusted G2G channel. | Medium | IMI is already GDPR-compliant; adds a defined procedure + legal basis. |
| **C. EU-level standard / regulation** | Extend the **Lead State concept** *into* the EU (currently third-country only) via a Council guideline, or a new "traveler protection" instrument making the notification registry interoperable across all member states. | High | Would codify the data-sovereignty principle at EU level. |

**Our proposal to the EU/countries:** adopt the EIS travel-notification registry as a voluntary
standard, transport over **eDelivery/AS4** (already-funded, open), and keep the **data-sovereignty
rule** (citizen data never leaves the home country). This is the smallest legal surface for the
biggest safety gain. Option A proves it bilaterally; Option B/C scales it.

---

## 7. MVP path

1. Build the **travel-notification registry** (home-country node, EUDI wallet sign-in) — no
   cross-border data.
2. Build the **alert-routing leg** over eDelivery/AS4 between two nodes (PT↔DE demo).
3. Deliver the **last-mile SMS + push** from the home country node.
4. Add **location disclosure** + "report closed" as opt-in features.
5. Satellite (Galileo EWSS / IRIS²) as a later resilience upgrade — not needed for the first
   working version.

---

## 8. Open questions (next research)

1. Which exact **eDelivery** Access Point / domain do we register for (member-state-level vs
   platform-level nodes)? Is ERCC/CECIS actually reusable for citizen alerting, or only for
   civil-protection resources?
2. Can a **new IMI procedure** be created without new legislation (Reg. 1024/2012 scope check)?
3. Is there an existing **EU travel-advisory** feed (e.g. consular travel advice) we should ingest
   instead of inventing a new one?
4. **GDPR legal basis** for the home country processing "citizen abroad" data — consent (from the
   wallet sign) vs public-interest (civil protection). Document both.
5. **SMS gateway** at scale — which provider/aggregator does a member-state-level node use, and
   does "roam like at home" cover emergency bulk SMS?
6. Satellite integration point — Galileo EWSS is *broadcast* (everyone), so it replaces leg 1's
   cell broadcast, not leg 3's targeted delivery. Confirm.

---

## 9. Sources

- ERCC / EU Civil Protection Mechanism: https://civil-protection-humanitarian-aid.ec.europa.eu/what/civil-protection/emergency-response-coordination-centre_en
- eDelivery (CEF building block, AS4): https://techsov-catalogue.eu/catalogue/solutions/european-commission/edelivery-building-block
- e-CODEX (e-Justice Communication via Online Data Exchange): https://interoperable-europe.ec.europa.eu/collection/open-source-observatory-osor/news/cross-border-justice-going-open-source
- Lead State concept — Council guidelines (2008/C317/06): https://europeanunion.diplomatie.belgium.be/sites/default/files/2023-05/The+EU's+role+on+Consular+crisis+management+-+Non-paper+by+Belgium,+Finland,+Luxembourg,+Poland+and+The+Netherlands.pdf
- Consular protection — Directive (EU) 2015/637: https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=celex:32015L0637
- IMI — Regulation (EU) 1024/2012: https://www.gov.uk/guidance/eu-internal-market-information-system
- EU-Alert / cell broadcast — ETSI TS 102 900: https://en.wikipedia.org/wiki/EU-Alert
- Galileo EWSS: https://www.euspa.europa.eu/galileo-ewss
- IRIS² / GOVSATCOM: https://defence-industry-space.ec.europa.eu/eu-space/iris2-secure-connectivity_en
