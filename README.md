# django-party

[![CI](https://github.com/DLRSP/django-party/actions/workflows/ci.yaml/badge.svg)](https://github.com/DLRSP/django-party/actions/workflows/ci.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/django-party.svg)](https://pypi.org/project/django-party/)

Shared party (person/organization) identity for Django sites: contacts, external ids, append-only consent ledger, and thin counterpart account codes.

Not a sales CRM. Not a double-entry ledger.

## Requirements

- Python 3.10+
- Django 4.2+

## Install

```bash
pip install django-party
```

```python
INSTALLED_APPS = [
    # ...
    "party",
    # ...
]
```

Then migrate:

```bash
python manage.py migrate party
```

## Concepts

| Model | Role |
|-------|------|
| `Party` | Canonical person or organization |
| `ExternalIdentity` | Multi-source ids (free `namespace`+`scheme`+`value`, e.g. PMS guest id vs fiscal supplier id) |
| `ContactPoint` / `PostalAddress` | Channels and addresses with validity |
| `ConsentRecord` | Append-only privacy/marketing ledger (`null` ≠ granted) |
| `PartyAccount` | Thin studio account-code metadata (no balances) |

## ExternalIdentity taxonomy

Pick **site-local** `namespace` / `scheme` strings. Examples:

| namespace | scheme | meaning |
|----------|--------|---------|
| `pms` | `guest` / `contact` / `company` | hospitality PMS ids |
| `fiscal` | `supplier` / `cedente` | fiscal facet primary key |
| `social` | `google` / `facebook` | IdP subject (auth link mirror) |

Same numeric `value` may exist under different `(namespace, scheme)` pairs. An open `(namespace, scheme, value)` binds to **one** Party.

Wire PMS/fiscal adapters in the **consumer** app — not inside `party.*`.

## Consent and account codes

- Write consent only via `record_consent()`; admin add/change/delete are closed.
- Never invent marketing consent from PMS privacy/promo payload keys (`refuse_untrusted_consent_mapping`).
- `PartyAccount.code` must be non-empty and **not** all-digit (PMS ids are not studio codes).

## License

MIT
