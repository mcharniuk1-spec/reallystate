# Tier-3 Fixture Templates

These templates define the fixture contract for Tier-3 connectors.

Rules:

- Fixtures must be synthetic/redacted.
- No live secrets, account identifiers, API tokens, or real personal data.
- Tests must parse these fixtures only; no live network dependency.

Template sets:

- `partner_feed/` -> Airbnb, Booking.com, Vrbo, Flat Manager, Menada
- `licensed_data/` -> AirDNA, Airbtics
- `official_register/` -> Property Register, KAIS
- `public_auction/` -> BCPEA property auctions
