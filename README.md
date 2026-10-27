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
| `ExternalIdentity` | Multi-source ids (`beddy`+`customer\|company\|contact`, `fiscal`+ supplier facet, …) |
| `ContactPoint` / `PostalAddress` | Channels and addresses with validity |
| `ConsentRecord` | Append-only privacy/marketing ledger (`null` ≠ granted) |
| `PartyAccount` | Thin studio account-code metadata (no balances) |

## License

MIT
