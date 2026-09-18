# 10 — Spain Validation (3rd destination country)

**Purpose:** validate the per-country model against a third country beyond the Germany/Portugal
pair. The question: does the "deadline clock + registration authority + landlord proof" pattern
generalize, or was it a DE/PT coincidence?

**Answer: it generalizes — and Spain adds a *third* distinct clock.**

---

## Fact matrix (verified)

| Fact | Spain |
|---|---|
| **Registration authority** | **Oficina de Extranjería** (Non-nationals Office) in the province of stay, or failing that the local **police station** (Comisaría). In person, appointment required. |
| **Registration timing (the clock)** | **Within 3 months of entry into Spain** (for stays >3 months). |
| **Registration document** | **Certificado de Registro de Ciudadano de la Unión** (CUE) — the "green certificate" / "green NIE". Issued immediately on registration; states name, nationality, address, NIE, and date of registration. |
| **Application form** | **EX-18** (Solicitud de inscripción en el Registro Central de Extranjeros). |
| **Fine** | **No monetary fine specified** for EU citizens (registration is a right, not penalty-backed like Germany's €1,000 Anmeldung fine). Late registration can complicate proving residence, but no stated penalty. |
| **Fee** | Tasa **modelo 790 código 012** (administrative fee, paid via form 790). |
| **Landlord/address proof** | **No specific landlord form.** Address shown via the registration + the **padrón** (see below). |
| **Tax ID** | **NIE** (Número de Identidad de Extranjero) — assigned on registration, printed on the certificate, and **doubles as the tax number (NIF)** for foreign residents. Self-employed additionally register at AEAT (Agencia Tributaria) for RETA. |
| **Health** | Employed → Spanish social security via employer. Self-sufficient / student → must show private health insurance or an S1. Pensioners/workers → S1 / EHIC. |
| **Residence permit (EU)** | **Not needed** — the green certificate *is* the residence registration. |
| **Separate local registration** | **Padrón / empadronamiento** at the town hall (Ayuntamiento) — required for the health card (tarjeta sanitaria) and most local services. Distinct from the CUE. |

## The three-clock contrast (why the platform needs per-country logic)

| | Germany | Portugal | **Spain** |
|---|---|---|---|
| Registration timing | **14 days** from move-in | **30 days after month 3** | **within 3 months** of entry |
| Fine | up to €1,000 | €400–1,500 | **none specified** |
| Authority | Bürgeramt | Câmara Municipal | Oficina de Extranjería / Policía |
| Landlord form | ✅ Wohnungsgeberbestätigung (§19 BMG) | (address proof via Junta/lease) | **none** (padrón instead) |
| Tax ID | Steuer-ID (auto, by post) | NIF (apply at Finanças) | **NIE (assigned with registration)** |

Three countries, three completely different clocks: **immediate (14 days)**, **deferred (30 days
after a threshold)**, and **window (3 months)**, plus three different tax-ID acquisition methods
(auto / apply / assigned-with-registration). This confirms the platform's core design assumption:
**every country's process decomposes into the same fact-matrix columns, but the values are
country-specific and must be curated per country.**

## What Spain also confirms

1. **Registration certificate ≠ residence permit.** EU citizens get a *registration* document
   (CUE), not a permit — same pattern as DE (Anmeldung) and PT (CRUE). The platform must never
   present these as "visas" or "permits."
2. **A second registration layer exists** (Spain's padrón) that DE/PT fold into one step. The data
   model needs to allow for **1..N registration steps** per country, not assume exactly one.
3. **Fee vs fine** are different columns — Spain has a fee (790-012) but no fine; DE has a fine;
   both need capturing.

## Sources (primary)

- Administración General del Estado — "Registering your residence" (Punto de Acceso General):
  https://administracion.gob.es/pag_Home/en/Tu-espacio-europeo/derechos-obligaciones/ciudadanos/residencia/obtencion-residencia/inscribirte-residente.html
- National Police — EU Citizen Registration Certificate (Form EX-18, fee 790-012):
  https://sede.policia.gob.es/portalCiudadano/_en/tramites_extranjeria_tramite_certificadoregistro_ciudadanoue.php
- Ajuntament de Barcelona — Certificate of registration as an EU national ("green NIE"):
  https://www.barcelona.cat/internationalwelcome/en/certificate-of-registration-as-an-eu-national
