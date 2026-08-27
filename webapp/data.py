"""
 EU Data Compass content dataset — Portugal-hosted instance (origin = Portugal).

Structure mirrors the data model in docs/02-spec/PLATFORM-SPEC.md §8:

    country -> intent (traveling|moving) -> subject -> {deadlines, documents, info}

Only Germany and Spain carry VERIFIED content (docs/04-research: TRAVELING-CASE, MOVING-CASE, DOCUMENTS-INDEX, SPAIN-VALIDATION). The other
seven destinations use the docs/04-research/COUNTRY-MATRIX.md, which is partly
UNVERIFIED — those are flagged `verified=False` so the UI can badge them as
mock/unverified. The short-stay (traveling) baseline is universal for EU
citizens (freedom of movement), so it is real for every destination.

No facts are invented here beyond what the docs record. Where a value is
unknown the string "—" or an explicit "UNVERIFIED" note is used.
"""

ORIGIN = {"code": "PT", "name": "Portugal", "flag": "🇵🇹"}

# ---------------------------------------------------------------------------
# Country registry — real focus = Germany. Spain is the second verified case.
# The rest come from the country matrix (docs/04-research/COUNTRY-MATRIX.md) and are marked unverified.
# ---------------------------------------------------------------------------

COUNTRIES = [
    {"code": "DE", "name": "Germany", "flag": "🇩🇪", "verified": True},
    {"code": "ES", "name": "Spain", "flag": "🇪🇸", "verified": True},
    {"code": "SK", "name": "Slovakia", "flag": "🇸🇰", "verified": False},
    {"code": "HU", "name": "Hungary", "flag": "🇭🇺", "verified": False},
    {"code": "SI", "name": "Slovenia", "flag": "🇸🇮", "verified": False},
    {"code": "HR", "name": "Croatia", "flag": "🇭🇷", "verified": False},
    {"code": "RO", "name": "Romania", "flag": "🇷🇴", "verified": False},
    {"code": "BG", "name": "Bulgaria", "flag": "🇧🇬", "verified": False},
    {"code": "GR", "name": "Greece", "flag": "🇬🇷", "verified": False},
    {"code": "CY", "name": "Cyprus", "flag": "🇨🇾", "verified": False},
]

# Subjects. Only "residence" is live for the MVP (per docs/01-plan/IMPLEMENTATION-PLAN.md build order).
SUBJECTS = [
    {"id": "residence", "name": "Residence & Registration", "icon": "🏠", "live": True},
    {"id": "work", "name": "Work", "icon": "💼", "live": False},
    {"id": "studies", "name": "Studies", "icon": "🎓", "live": False},
    {"id": "tax", "name": "Tax", "icon": "🧾", "live": False},
    {"id": "health", "name": "Health", "icon": "🏥", "live": False},
    {"id": "social_security", "name": "Social security", "icon": "🛟", "live": False},
    {"id": "vehicle", "name": "Vehicle", "icon": "🚗", "live": False},
    {"id": "family", "name": "Family", "icon": "👪", "live": False},
]

INTENTS = [
    {"id": "traveling", "name": "Traveling", "sub": "Short stay (< 3 months)", "icon": "🧳"},
    {"id": "moving", "name": "Moving in", "sub": "Long stay / relocation", "icon": "📦"},
]


# ---------------------------------------------------------------------------
# Universal short-stay baseline (freedom of movement — verified, docs/04-research/TRAVELING-CASE.md).
# Same for every destination for EU citizens.
# ---------------------------------------------------------------------------

def _traveling_residence(dest_name):
    return {
        "verified": True,
        "summary": (
            f"As an EU citizen you need **no visa and no residence permit** to enter or stay in "
            f"{dest_name} for up to **3 months**. A valid national ID or passport is the only hard "
            f"requirement. No registration is needed for a short, temporary stay."
        ),
        "deadlines": [
            {"trigger": "Day 0 — arrival", "action": "Nothing to register", "window": "—", "fine": "—"},
            {"trigger": "Day 90 (3 months)", "action": "Right to stay becomes conditional", "window": "assess", "fine": "—"},
            {"trigger": "If residence moves", "action": f"Registration clock starts (see Moving)", "window": "per country", "fine": "per country"},
        ],
        "documents": [
            {
                "name": "Valid national ID / passport",
                "initial_info": "Proof of EU citizenship and identity. The only hard requirement for a short stay.",
                "shared": "Identity, nationality",
                "to_whom": "Presented on request (no submission)",
                "retention": "n/a — carried by you",
                "reissuable": "Yes (issuing authority in Portugal)",
                "submit_where": "Kept on person",
                "issuer": "Portugal",
                "form_url": None,
            },
            {
                "name": "EHIC (European Health Insurance Card)",
                "initial_info": "Covers necessary state healthcare during a temporary stay on the same terms as locals.",
                "shared": "Identity, insurance status",
                "to_whom": "Shown at doctor / hospital",
                "retention": "Card validity period",
                "reissuable": "Yes",
                "submit_where": "Health provider / Segurança Social (Portugal)",
                "issuer": "Portuguese health provider",
                "form_url": "https://ehic.europa.eu/",
            },
            {
                "name": "Private travel insurance (optional)",
                "initial_info": "Extra coverage — repatriation, luggage, cancellation. Not required.",
                "shared": "As per insurer",
                "to_whom": "Insurer",
                "retention": "Policy period",
                "reissuable": "Yes",
                "submit_where": "Any insurer",
                "issuer": "Any insurer",
                "form_url": None,
            },
        ],
        "info": [
            ("Short-stay right", "≤ 3 months, valid ID only, no conditions", "Freedom of Movement Act/EU"),
            ("Visa / residence permit", "Not needed for EU citizens", "Freedom of Movement Act/EU (2005)"),
            ("Healthcare", "EHIC covers necessary care during the stay", "ehic.europa.eu"),
            ("If the trip becomes a move", "Destination's registration clock activates — see the Moving intent", "docs/04-research/MOVING-CASE.md"),
        ],
        "sources": [
            "EU freedom of movement — https://europa.eu/youreurope/citizens/residence/",
            "EHIC — https://ehic.europa.eu/",
        ],
    }


# ---------------------------------------------------------------------------
# Germany — VERIFIED moving case (docs/04-research/MOVING-CASE.md, DOCUMENTS-INDEX.md). The real focus.
# ---------------------------------------------------------------------------

_DE_MOVING = {
    "verified": True,
    "summary": (
        "Germany registers residence **immediately on move-in**: everyone (Germans included) must "
        "file an **Anmeldung** at the local **Bürgeramt** within **14 days** of moving in — fine up "
        "to **€1,000** if missed. There is no 3-month grace period. A **Wohnungsgeberbestätigung** "
        "(landlord confirmation) is required and the tenancy agreement does *not* replace it (§19 BMG). "
        "No residence permit is needed (freedom of movement)."
    ),
    "deadlines": [
        {"trigger": "Move-in", "action": "Anmeldung at Bürgeramt", "window": "14 days", "fine": "up to €1,000"},
        {"trigger": "After Anmeldung", "action": "Steuer-ID arrives by post (automatic)", "window": "~1–2 weeks", "fine": "—"},
        {"trigger": "Start work", "action": "Health insurance + social security", "window": "before/as of start", "fine": "legal requirement"},
        {"trigger": "5 years residence", "action": "Permanent right of residence", "window": "—", "fine": "—"},
    ],
    "documents": [
        {
            "name": "Wohnungsgeberbestätigung (landlord confirmation)",
            "initial_info": "Confirms you moved into the dwelling. Required for Anmeldung; the lease alone is NOT accepted (§19(3) BMG).",
            "shared": "Name, address, move-in date, landlord identity",
            "to_whom": "Bürgeramt (via you, at Anmeldung)",
            "retention": "Held in the registration record",
            "reissuable": "Yes (landlord re-signs)",
            "submit_where": "Bürgeramt appointment",
            "issuer": "Landlord / agent",
            "form_url": "assets/pdf/wohnungsgeberbestaetigung_berlin.pdf",
        },
        {
            "name": "Anmeldung → Meldebescheinigung (registration)",
            "initial_info": "The address registration itself. Produces the Meldebescheinigung (proof of address) needed for banking, tax, etc.",
            "shared": "Name, nationality, address, move-in date, family",
            "to_whom": "Bürgeramt / Meldebehörde",
            "retention": "Municipal register (ongoing while resident)",
            "reissuable": "Yes (request a new certificate)",
            "submit_where": "Local Bürgeramt (in person or via power of attorney)",
            "issuer": "Bürgeramt",
            "form_url": None,
        },
        {
            "name": "Steuer-ID (tax identification number)",
            "initial_info": "Assigned automatically after Anmeldung and sent by post. No separate application.",
            "shared": "Identity linked to tax record",
            "to_whom": "Federal Central Tax Office (BZSt)",
            "retention": "Permanent tax identifier",
            "reissuable": "Re-notification possible",
            "submit_where": "Automatic — arrives by post",
            "issuer": "BZSt",
            "form_url": None,
        },
        {
            "name": "Health insurance membership",
            "initial_info": "Mandatory. Join a public Krankenkasse (TK/AOK/Barmer…) or private if eligible. Employer usually registers you.",
            "shared": "Identity, employment, address",
            "to_whom": "Public/private insurer",
            "retention": "Membership duration",
            "reissuable": "Yes",
            "submit_where": "Insurer",
            "issuer": "Public/private insurer",
            "form_url": None,
        },
        {
            "name": "Rentenversicherungsnummer (social security number)",
            "initial_info": "Issued via employer / Deutsche Rentenversicherung. Needed for payroll contributions.",
            "shared": "Identity, employment",
            "to_whom": "Deutsche Rentenversicherung",
            "retention": "Permanent",
            "reissuable": "Yes",
            "submit_where": "Via employer / pension fund",
            "issuer": "Deutsche Rentenversicherung",
            "form_url": None,
        },
        {
            "name": "Bank account (IBAN)",
            "initial_info": "Needed for salary. Requires Anmeldung/Meldebescheinigung + ID.",
            "shared": "Identity, address",
            "to_whom": "Bank",
            "retention": "Account lifetime",
            "reissuable": "n/a",
            "submit_where": "Bank",
            "issuer": "Bank",
            "form_url": None,
        },
    ],
    "info": [
        ("Anmeldung window", "14 days from move-in", "§17 Bundesmeldegesetz (BMG)"),
        ("Anmeldung fine", "up to €1,000", "BMG"),
        ("Landlord confirmation", "Required; lease ≠ confirmation", "§19(3) BMG"),
        (">3-month conditions", "work / training / job-seeking / means+insurance / student / 5yr", "EU Equal Treatment Office"),
        ("Tax ID", "Auto-assigned after Anmeldung", "BZSt"),
        ("Residence permit", "Not needed for EU citizens", "Freedom of Movement Act/EU"),
        ("Permanent residence", "After 5 years legal residence", "EU Equal Treatment Office"),
    ],
    "sources": [
        "EU Equal Treatment Office (Germany) — https://www.eu-gleichbehandlungsstelle.de/eugs-en/eu-citizens/information-center/residence",
        "Make it in Germany — https://www.make-it-in-germany.com/en/working-in-germany/information-eu-citizens",
        "Wohnungsgeberbestätigung form (Berlin) — assets/pdf/wohnungsgeberbestaetigung_berlin.pdf",
    ],
}


# ---------------------------------------------------------------------------
# Spain — VERIFIED moving case (docs/04-research/SPAIN-VALIDATION.md).
# ---------------------------------------------------------------------------

_ES_MOVING = {
    "verified": True,
    "summary": (
        "Spain uses a **3-month window**: EU citizens staying >3 months register at the **Oficina de "
        "Extranjería** (or police station) **within 3 months of entry**, using form **EX-18**. You "
        "receive the **Certificado de Registro de Ciudadano de la Unión** (CUE, the 'green "
        "certificate'), which carries your **NIE** — this doubles as your tax number. There is **no "
        "specific fine** for EU citizens and **no landlord form**; a separate **padrón** registration "
        "at the town hall is needed for the health card and local services."
    ),
    "deadlines": [
        {"trigger": "Entry into Spain", "action": "Register at Oficina de Extranjería (form EX-18)", "window": "within 3 months", "fine": "none specified"},
        {"trigger": "At registration", "action": "NIE assigned + printed on the CUE", "window": "same appointment", "fine": "—"},
        {"trigger": "For local services / health card", "action": "Padrón (empadronamiento) at the Ayuntamiento", "window": "as needed", "fine": "—"},
    ],
    "documents": [
        {
            "name": "EX-18 — Registration application",
            "initial_info": "Solicitud de inscripción en el Registro Central de Extranjeros — the application to register as an EU resident.",
            "shared": "Identity, nationality, address",
            "to_whom": "Oficina de Extranjería / Policía Nacional",
            "retention": "Central Register of Foreigners",
            "reissuable": "Yes",
            "submit_where": "Oficina de Extranjería (appointment) or Comisaría",
            "issuer": "Ministerio del Interior",
            "form_url": None,
        },
        {
            "name": "Certificado de Registro (CUE / 'green certificate')",
            "initial_info": "Issued immediately on registration. States name, nationality, address, NIE and date of registration. Is NOT a residence permit.",
            "shared": "Identity, nationality, address, NIE",
            "to_whom": "Held by you as proof of registration",
            "retention": "No expiry",
            "reissuable": "Yes",
            "submit_where": "Issued at the registration office",
            "issuer": "Oficina de Extranjería",
            "form_url": None,
        },
        {
            "name": "Tasa modelo 790 código 012 (fee)",
            "initial_info": "Administrative fee paid via form 790 before/at registration.",
            "shared": "Identity, payment",
            "to_whom": "Agencia Tributaria / bank",
            "retention": "n/a",
            "reissuable": "n/a",
            "submit_where": "Bank / online (form 790)",
            "issuer": "Agencia Tributaria",
            "form_url": None,
        },
        {
            "name": "Padrón (empadronamiento)",
            "initial_info": "Separate town-hall registration of local residence. Required for the health card (tarjeta sanitaria) and most local services.",
            "shared": "Name, address",
            "to_whom": "Ayuntamiento (town hall)",
            "retention": "Municipal register",
            "reissuable": "Yes",
            "submit_where": "Ayuntamiento",
            "issuer": "Ayuntamiento",
            "form_url": None,
        },
    ],
    "info": [
        ("Registration timing", "Within 3 months of entry", "Administración General del Estado"),
        ("Fine", "None specified for EU citizens (registration is a right)", "docs/04-research/SPAIN-VALIDATION.md"),
        ("Fee", "Tasa modelo 790 código 012", "Policía Nacional"),
        ("Landlord form", "None — address via registration + padrón", "docs/04-research/SPAIN-VALIDATION.md"),
        ("Tax ID", "NIE assigned with registration; doubles as NIF", "AEAT"),
        ("Residence permit", "Not needed — the CUE is the registration", "docs/04-research/SPAIN-VALIDATION.md"),
        ("Second layer", "Padrón at the Ayuntamiento is a distinct step", "docs/04-research/SPAIN-VALIDATION.md"),
    ],
    "sources": [
        "Administración General del Estado — https://administracion.gob.es/pag_Home/en/Tu-espacio-europeo/derechos-obligaciones/ciudadanos/residencia/obtencion-residencia/inscribirte-residente.html",
        "Policía Nacional (EX-18, 790-012) — https://sede.policia.gob.es/portalCiudadano/_en/tramites_extranjeria_tramite_certificadoregistro_ciudadanoue.php",
        "Ajuntament de Barcelona — https://www.barcelona.cat/internationalwelcome/en/certificate-of-registration-as-an-eu-national",
    ],
}


# ---------------------------------------------------------------------------
# The country matrix (docs/04-research/COUNTRY-MATRIX.md). UNVERIFIED where the doc says so.
# Built from the master fact table so the UI can show real structure with a
# mock/unverified badge.
# ---------------------------------------------------------------------------

_MATRIX = {
    "SK": {
        "authority": "Foreign Police Department (Oddelenie cudzineckej polície)",
        "timing": "Two-step: report start/place of stay within 10 working days of entry; if staying >3 months, register within 30 days after the 3-month mark",
        "fine": "UNVERIFIED (no amount in primary source)",
        "landlord": "Notarised owner affidavit / consent / tenancy agreement / accommodation-facility confirmation",
        "tax_id": "DIČ via tax office (Daňový úrad) — apply; also rodné číslo",
        "health": "Health insurance mandatory (VšZP/Dôvera/Union)",
        "permit": "Not needed — optional Residence Card of an EU Citizen (10 yrs, €10/€39)",
        "source": "https://www.minv.sk/?residence-of-an-foreigner=",
    },
    "HU": {
        "authority": "National Directorate-General for Aliens Policing (OIF)",
        "timing": "Notify residence at latest on the 93rd day from date of entry",
        "fine": "UNVERIFIED (no amount on OIF page)",
        "landlord": "Lease / title deed / other proof — no special landlord form; address card (lakcímkártya) mailed automatically",
        "tax_id": "adóazonosító jel via NAV — apply; TAJ number for health",
        "health": "TAJ social-security/health number via NEAK; EHIC/S1",
        "permit": "Not needed — registration certificate (HUF 1,000, indefinite)",
        "source": "https://oif.gov.hu/factsheets/registration-certificate-for-eea-nationals",
    },
    "SI": {
        "authority": "Administrative Unit (Upravna enota) of residence",
        "timing": "Apply within 3 months of entry (can apply immediately)",
        "fine": "UNVERIFIED (not on gov.si)",
        "landlord": "Proof of accommodation required — no named landlord form",
        "tax_id": "davčna številka via FURS — apply; EMŠO personal number",
        "health": "Adequate health insurance required (ZZZS); EHIC/S1",
        "permit": "Not needed — residence registration certificate (≤5 yrs)",
        "source": "https://www.gov.si/en/topics/entry-and-residence/",
    },
    "HR": {
        "authority": "Police administration / station (policijska uprava/postaja)",
        "timing": "Register temporary stay within 8 days after expiry of the 3-month stay (Obrazac 1b)",
        "fine": "UNVERIFIED (not on MUP page)",
        "landlord": "Proof of accommodation + health-insurance proof + sufficient means",
        "tax_id": "OIB via Porezna uprava — apply, free (~8 days)",
        "health": "Health-insurance proof required at registration (HZZO); EHIC/S1",
        "permit": "Not needed — certificate free; optional residence card €13.27 (5 yrs)",
        "source": "https://mup.gov.hr/",
    },
    "RO": {
        "authority": "General Inspectorate for Immigration (IGI)",
        "timing": "Register residency within 3 months (staying >3 months)",
        "fine": "UNVERIFIED (not on IGI page)",
        "landlord": "Proof of residence/address required — no named landlord form",
        "tax_id": "CNP assigned at registration; tax registration via ANAF (NIF if no CNP) — apply",
        "health": "Health insurance (CNAS); EHIC/S1",
        "permit": "Not needed — registration certificate same day (≤5 yrs)",
        "source": "https://igi.mai.gov.ro/en/residence-registration/",
    },
    "BG": {
        "authority": "Migration Directorate, Ministry of Interior",
        "timing": "Apply for certificate of residence within 3 months from date of entry",
        "fine": "UNVERIFIED",
        "landlord": "Address proof required (address registration); specifics UNVERIFIED",
        "tax_id": "Personal number (ЛНЧ/ЕГН) + tax registration via NRA — apply",
        "health": "Health insurance (NHIF/НЗОК); EHIC/S1",
        "permit": "Not needed — residence certificate (fee UNVERIFIED)",
        "source": "https://www.mvr.bg/migration/en/legislation/citizens-of-eu",
    },
    "GR": {
        "authority": "Hellenic Police — Aliens Directorates / Security & Police Depts",
        "timing": "For stays >3 months: appear in person after expiry of the 3-month period",
        "fine": "UNVERIFIED (not on MITOS page)",
        "landlord": "Proof of address required — no named landlord form",
        "tax_id": "AFM (ΑΦΜ) via DOY/AADE — apply (free); AMKA social-security no.",
        "health": "AMKA (health/EFKA/EOPYY); EHIC/S1",
        "permit": "Not needed — registration certificate (fee €0.50, indefinite)",
        "source": "https://www.gov.gr/en/sdg/residence/temporary-or-permanent-move/general/obligation-for-citizens-to-register-their-residence-for-periods-exceeding-three-months",
    },
    "CY": {
        "authority": "Civil Registry and Migration Department (CRMD)",
        "timing": "Apply for Registration Certificate (MEU1) within 4 months from date of entry",
        "fine": "up to €2,500 (confirmed, gov.cy)",
        "landlord": "Proof of address required — no named landlord form",
        "tax_id": "TIC via Tax Department — apply; Social Insurance no. if employed",
        "health": "Comprehensive sickness insurance required for inactive; GESY; EHIC/S1",
        "permit": "Not needed — MEU1 'Yellow Slip' (fee €20, no expiry)",
        "source": "https://www.gov.cy/moi/en/residence-cards/",
    },
}


def _matrix_moving(code):
    """Build a moving-case dashboard from the docs/04-research/COUNTRY-MATRIX.md row (unverified)."""
    m = _MATRIX[code]
    return {
        "verified": False,
        "summary": (
            f"**Rough / unverified data** from the 8-country registration matrix (docs/04-research/COUNTRY-MATRIX.md). "
            f"EU citizens need **no residence permit** (freedom of movement) — a registration "
            f"certificate only. Registration authority: **{m['authority']}**. "
            f"Timing: {m['timing']}."
        ),
        "deadlines": [
            {"trigger": "Entry / move-in", "action": f"Register at {m['authority']}", "window": m["timing"], "fine": m["fine"]},
            {"trigger": "For tax", "action": m["tax_id"], "window": "—", "fine": "—"},
            {"trigger": "For health", "action": m["health"], "window": "—", "fine": "—"},
        ],
        "documents": [
            {
                "name": "Registration certificate",
                "initial_info": m["permit"],
                "shared": "Identity, nationality, address",
                "to_whom": m["authority"],
                "retention": "UNVERIFIED",
                "reissuable": "UNVERIFIED",
                "submit_where": m["authority"],
                "issuer": m["authority"],
                "form_url": None,
            },
            {
                "name": "Address / accommodation proof",
                "initial_info": m["landlord"],
                "shared": "Address",
                "to_whom": m["authority"],
                "retention": "UNVERIFIED",
                "reissuable": "UNVERIFIED",
                "submit_where": m["authority"],
                "issuer": "Landlord / authority",
                "form_url": None,
            },
        ],
        "info": [
            ("Registration authority", m["authority"], m["source"]),
            ("Timing (deadline clock)", m["timing"], m["source"]),
            ("Fine", m["fine"], m["source"]),
            ("Tax ID", m["tax_id"], m["source"]),
            ("Health / social", m["health"], m["source"]),
            ("Residence permit", m["permit"], m["source"]),
        ],
        "sources": [f"Primary — {m['source']}", "Cross-check: docs/04-research/COUNTRY-MATRIX.md"],
    }


# ---------------------------------------------------------------------------
# Assembly: content[country_code][intent_id][subject_id]
# ---------------------------------------------------------------------------

def get_country(code):
    for c in COUNTRIES:
        if c["code"] == code:
            return c
    return None


def get_content(country_code, intent_id, subject_id):
    """Return the dashboard dict for a (country, intent, subject), or None."""
    if subject_id != "residence":
        return None  # only residence is live in the MVP

    country = get_country(country_code)
    if not country:
        return None

    if intent_id == "traveling":
        return _traveling_residence(country["name"])

    # moving
    if country_code == "DE":
        return _DE_MOVING
    if country_code == "ES":
        return _ES_MOVING
    if country_code in _MATRIX:
        return _matrix_moving(country_code)
    return None
