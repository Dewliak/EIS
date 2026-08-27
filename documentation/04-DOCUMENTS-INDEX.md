# 04 — Documents & Information Index (Master)

Master tables for the platform's **Documents** and **Information** tabs.
**Case: Portugal → Germany** (Portuguese citizens).

## A. Documents needed (both cases)

| Document | Travel | Move | Issuer | Form/Portal |
|---|---|---|---|---|
| Valid national ID / passport | ✅ | ✅ | Portugal | — |
| EHIC (health card) | ✅ (rec) | bridging | Portuguese health provider | ehic.europa.eu |
| Wohnungsgeberbestätigung (landlord confirmation) | — | ✅ | Landlord / agent | §19(3) BMG form (PDF) |
| Anmeldung → Meldebescheinigung (registration) | — | ✅ | Bürgeramt | local Bürgeramt appointment |
| Steuer-ID (tax ID) | — | ✅ (auto) | BZSt (Federal Central Tax Office) | automatic by post |
| Health insurance membership | — | ✅ | Public/private insurer | TK/AOK/Barmer/etc. |
| Rentenversicherungsnummer (social security) | — | ✅ | Pension fund / insurer | Deutsche Rentenversicherung |
| Employment contract | — | ✅ | Employer | — |
| Bank account (IBAN) | — | ✅ | Bank | — |
| Driving licence exchange | — | optional | Führerscheinstelle | — |

> Note: **no residence permit** for EU citizens in Germany (freedom of movement).

## B. Information fields to collect (per user)

### For traveling
- Country of origin (Portugal), destination (Germany)
- Intended length of stay (days)
- Purpose (tourism / conference / business)
- Health coverage (EHIC? private?)
- Whether the trip may become a relocation

### For moving
- Country of origin (Portugal), destination (Germany)
- Date of move-in (starts the 14-day Anmeldung clock)
- Employment status + contract type
- Which >3-month condition applies (employed / self-employed / training / job-seeking / means+insurance / student)
- Address + landlord details (for Wohnungsgeberbestätigung)
- Family members + nationalities
- Health insurance status
- Vehicle (driving licence exchange?)

## C. Key rules & thresholds (the "Information" tab content)

| Rule | Value | Source |
|---|---|---|
| Short stay right | ≤3 months, valid ID only, no conditions | Freedom of Movement Act/EU; EU Equal Treatment Office |
| No visa/residence permit | EU citizens | Freedom of Movement Act/EU (2005) |
| Anmeldung window | 14 days from move-in | §17 Bundesmeldegesetz (BMG) |
| Anmeldung fine | up to €1,000 | BMG |
| Landlord confirmation | required; lease ≠ confirmation | §19(3) BMG |
| >3-month conditions | work / training / job-seeking / means+insurance / student / 5yr | EU Equal Treatment Office |
| Tax ID | auto-assigned after Anmeldung | BZSt |
| Permanent residence | after 5 years legal residence | EU Equal Treatment Office |

## D. Authority map (who does what)

| Authority | Role |
|---|---|
| **Bürgeramt / Meldebehörde** | Anmeldung, Meldebescheinigung |
| **Ausländerbehörde** (foreigners authority) | verifies freedom-of-movement conditions if requested |
| **BZSt (Bundeszentralamt für Steuern)** | Steuer-ID |
| **Deutsche Rentenversicherung** | social security number (RVNR) |
| **Public health insurer (Krankenkasse)** | health insurance |
| **Finanzamt** | income tax (after Steuer-ID) |
| **Führerscheinstelle** | driving licence exchange |

## E. Contrast: Germany vs Portugal (why the platform needs per-country logic)

| Aspect | Germany | Portugal |
|---|---|---|
| Registration timing | **14 days** from move-in | 30 days after **month 3** |
| Registration doc | Anmeldung → Meldebescheinigung | CRUE |
| Where | Bürgeramt | Câmara Municipal |
| Landlord confirmation | ✅ required (§19 BMG) | (address proof via Junta/lease) |
| Tax ID | auto after Anmeldung | NIF (apply at Finanças) |
| Residence permit (EU) | not needed | not needed |

This table is the exact kind of logic the platform surfaces so users don't get caught by the
different clocks.
