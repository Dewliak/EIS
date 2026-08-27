# 07 — Assisting Platforms (existing tools to leverage / mirror)

Platforms that already help users navigate EU/DE/PT bureaucracy. Two purposes: (1) reference for
correctness, (2) possible data sources to integrate.

## Official EU portals

| Platform | URL | What it does |
|---|---|---|
| **Your Europe** | europa.eu/youreurope | Central EU rights portal — travel, residence, work, health, tax, vehicles. Closest existing equivalent to our concept. |
| **EURES** | eures.europa.eu | Job mobility, living/working conditions per country |
| **SOLVIT** | ec.europa.eu/solvit | Free problem-solving when EU rights are denied |
| **e-Justice Portal** | e-justice.europa.eu | Legal forms, judicial procedures |
| **EHIC portal** | ehic.europa.eu | European Health Insurance Card info |

## Germany portals (destination)

| Platform | URL | What it does |
|---|---|---|
| **Make it in Germany** | make-it-in-germany.com | Federal portal: work, visas, recognition, EU-citizen info |
| **EU Equal Treatment Office (EU-Gleichbehandlungsstelle)** | eu-gleichbehandlungsstelle.de | Official info for EU citizens in Germany (residence, tax, insurance, work) |
| **Auswärtiges Amt (Foreign Office)** | auswaertiges-amt.de | Visa/residence FAQ for EU citizens |
| **Bundesregierung / service.bund.de** | service.bund.de | Federal service portal |
| **service.berlin.de** | service.berlin.de | Berlin Bürgeramt: Anmeldung appointments + forms |
| **Deutsche Rentenversicherung** | deutsche-rentenversicherung.de | Social security / pension |
| **BZSt (Federal Central Tax Office)** | bzst.de | Steuer-ID |

## Portugal portals (origin — reference)

| Platform | URL | What it does |
|---|---|---|
| **gov.pt** | gov.pt | Central public-services portal |
| **ePortugal** | eportugal.gov.pt | Citizen/business services catalogue |
| **AIMA** | aima.gov.pt | Migration agency (ex-SEF) |
| **Portal das Finanças** | portaldasfinancas.gov.pt | Tax (NIF) |
| **Segurança Social** | seg-social.pt | Social security / EHIC |

## Third-party aggregators (competitive reference)

| Platform | URL | Angle |
|---|---|---|
| All About Berlin | allaboutberlin.com | Berlin bureaucracy guides + templates |
| GermanyCompass | germanycompass.com | Anmeldung, registration |
| expats.de | expats.de | Germany bureaucracy guides |
| Simple Germany | simplegermany.com | Social security, health, registration |
| Anchorless / Nomad Gate / Portugalist | anchorless.io / nomadgate.com / portugalist.com | Portugal moving guides |

## What we do differently
- **Unified interface** across all EU countries (these are mostly single-country).
- **Intent split** (travel vs move) + **per-country deadline clock** — e.g. Germany's 14-day
  Anmeldung vs Portugal's 30-day-after-month-3 CRUE. The clocks are the killer pain point.
- **EUDI Wallet integration** → travel notification + emergency system (nobody has this yet).

## Integration notes
- Your Europe / Make-it-in-Germany are **content sources**, not APIs — curate or link.
- No single public "mobility API"; data must be curated per country.
- eIDAS/EUDI Wallet has a defined technical spec (ARF) for our travel-notification feature.
