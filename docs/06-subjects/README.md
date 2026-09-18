# Subjects — research for the 7 "coming soon" categories

Fills the `webapp/data.py` `SUBJECTS` list (residence is already live). Each subject has two
sections: **Traveling (<3 months)** and **Moving (>3 months)**, matching the `intent` split.

Content model (maps 1:1 to `data.py` `get_content`):
`deadlines[]` · `documents[]{name, initial_info, shared, to_whom, retention, reissuable,
submit_where, issuer, form_url}` · `info[]` · `sources[]`.

**Origin = Portugal, destination = Germany** (the verified case).

| Subject | File | data.py id |
|---|---|---|
| Work | `work.md` | `work` |
| Studies | `studies.md` | `studies` |
| Tax | `tax.md` | `tax` |
| Health | `health.md` | `health` |
| Social security | `social-security.md` | `social_security` |
| Vehicle | `vehicle.md` | `vehicle` |
| Family | `family.md` | `family` |

Note: these overlap the **case** docs (`../03-cases/cases/`) but are the **subject/topic** cut —
e.g. "Health" applies to *every* moving case (worker, student, retiree…), not just one.
