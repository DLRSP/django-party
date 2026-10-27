party 0.1.2 (2026-10-28)
========================

No significant changes.


=========
Changelog
=========

0.3.0 (2026-10-27)
------------------

* Add ``PartyFact`` (keyed attributes with validity) and ``upsert_party_fact`` /
  ``close_party_fact``; refuse fiscal/token fact keys.
* Document ExtId namespace ``socialprofile`` for auth IdP links.
* Seed CRM feature Groups ``dlrsp:crm.contacts_*`` (and consent / account HITL)
  on ``post_migrate`` (empty assignment — Admin assigns).

0.2.0 (2026-10-27)
------------------

* Consent refuse helper is settings-driven
  (``PARTY_CONSENT_FORBIDDEN_PAYLOAD_KEYS``, default empty); removed
  Beddy-named public alias.
* ``PartyAccount.save()`` enforces non-empty, non-all-digit codes.
* ``ConsentRecord`` queryset blocks ``_update`` / ``_raw_delete`` as well as
  public ``update`` / ``delete``.

0.1.1 (2026-10-27)
------------------

* Align test harness with fleet layout: ``tests/`` + ``tests.settings`` +
  ``runtests.py`` (replaces non-standard ``party_tests`` package).
* English-only identifiers and docs in the package surface.

0.1.0 (2026-10-27)
------------------

* Initial public release: Party, ExternalIdentity, ContactPoint, PostalAddress,
  ConsentRecord (append-only), PartyAccount, PartyMergeEvent.


.. note:: 0.1.2 was a local pre-release line absorbed into 0.2.0.
