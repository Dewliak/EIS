# 06 — PDF URLs & Forms

Direct links to PDF documents/forms. Fetched assets under `../assets/pdf/`.

## Fetched (saved locally)

| File | Source | Status |
|---|---|---|
| `../assets/pdf/wohnungsgeberbestaetigung_berlin.pdf` | Berlin landlord-confirmation form (§19(3) BMG), 1p DE | ✅ downloaded & text-extracted |
| `../assets/pdf/crue_form_porto.pdf` | Portugal CRUE form + guide (2pp PT) — *reverse direction, kept as reference* | ✅ downloaded & text-extracted |

- **Germany (current case):** https://www.berlinstadtservice.de/pdf/Wohnungsgeberbescheinigung.pdf
- **Portugal (reference):** https://portaldomunicipe.cm-porto.pt/documents/20122/1130484/fol_sef_PT.pdf/b3dfd875-90f6-9857-b62c-69b250b09aaa?t=1701336803152

## Known PDF/form URLs (not yet fetched)

- **Wohnungsgeberbestätigung (other cities)** — each municipality posts its own; Berlin is the
  template. Note: some city portals (e.g. service.berlin.de) require browser/JS.
- **Anmeldung appointment** — not a PDF; booked online at the local Bürgeramt
  (e.g. service.berlin.de for Berlin).

## Where to find more (per document)

| Document | Where to fetch |
|---|---|
| Wohnungsgeberbestätigung | Landlord signs the form (city-provided template) |
| Anmeldung / Meldebescheinigung | Bürgeramt (in person) — book online |
| Steuer-ID | automatic by post after Anmeldung (BZSt) |
| Health insurance | insurer website (TK, AOK, Barmer, etc.) |
| Social security number (RVNR) | via employer / Deutsche Rentenversicherung |
| Driving licence exchange | Führerscheinstelle (local) |

## Fetch notes
- Both PDFs fetched via curl (76 KB & 49 KB), text extracted into the case docs.
- AIMA.gov.pt (Portugal) blocks curl (anti-bot) — PDFs there need a browser session.
- No fabricated URLs — only links confirmed to exist in search results or page content.
