# 00 — Platform Concept

> Note: this is the early concept doc. **`09-FULL-PLATFORM-SPEC.md`** is the consolidated master
> specification (web + mobile + EUDI + emergency, full data model, research plan). Start there.

## Vision
One interface for every EU country. A user selects a country, says whether they are
**traveling** or **moving in**, picks a subject category, and lands in structured tabs:
**Deadlines · Documents · Information**. No more hunting across government sites.

## User flow (proposed)
```
1. Landing dashboard
   └─ country picker (all 27 EU + EEA/CH)
2. Intent
   └─ Traveling (short stay)  OR  Moving in (long stay)
3. Subject category
   └─ e.g. Residence · Tax · Work · Health · Social security · Vehicle · Family
4. Tabbed result view
   ├─ Deadlines   (when each step is due — e.g. "CRUE within 30 days after month 3")
   ├─ Documents   (which forms, what to fill in, where to get them)
   └─ Information (rules, conditions, fees, fines, contacts)
```

## Why the tabs matter
- **Deadlines** = the compliance clock. Fines hit hard — Germany's Anmeldung is up to €1,000,
  Portugal's CRUE window is €400–1,500 — this is exactly the "pain point" the platform kills.
- **Documents** = the checklist. Forms (PDF), what fields they need, which authorities issue them.
- **Information** = rules, conditions (freedom-of-movement conditions per country), fees, exceptions, contacts.

## Future: EUDI Wallet integration (eIDAS 2.0)
The European Digital Identity Wallet is the unlock for two features we've planned:

1. **Travel notification** — inform the destination country (and origin) that you are
   traveling there for a specific period. Wallet = trusted digital identity, so the
   notification is cryptographically verifiable.
2. **Emergency system** — in an emergency, authorities can validate who you are and where
   you're from instantly (no physical documents). Wallet attributes (identity, address,
   age) are verified at source.

Timeline: wallets mandatory from **24 Dec 2026**; regulated entities accept from ~late 2027.
See `08-EUDI-WALLET.md`.

## MVP scope (for now)
User asked to start with **documents + questions** — i.e. the *Documents* and *Information*
tabs, built from the index in `04-DOCUMENTS-INDEX.md`. The worked example is
**Portugal → Germany** (Portuguese citizens).

## Data model sketch (for later)
```
country(id, name, code)
intent(traveling | moving)
subject(residence | tax | work | health | social_security | vehicle | family)
step(id, country_id, intent, subject, name, due_rule, authority, cost, fine)
document(id, step_id, name, form_url, fields[], issuer)
info(id, step_id, content, source_url)
```
