# ServeoPOS v0.1.0-beta Release Notes

Release date: 2025-12-04

Summary
- Initial beta release implementing a comprehensive POS feature set for restaurants.

Key features included in this beta
- Product catalog with categories and barcode mapping
- Orders: create, parallel/hold, delayed orders, order items and notes
- Payments: payment methods, payment transactions, split bills, checkout flow
- Loyalty: loyalty cards, points accrual and redemption
- E-wallet: prepaid wallet top-ups and transactions
- Tables & floor plan: table listing, assign/transfer, bookings
- Kiosk: self-service kiosk menu endpoint
- Kitchen Display System (KDS): pending orders endpoint
- Receipts: generation and print status
- Cash register: open/close and reconciliation
- Offline support: order sync endpoint

Known issues & notes
- Alembic migrations in `migrations/versions` are present but contain numeric revision identifiers; running `flask db upgrade` in some environments may fail due to revision id mapping (KeyError '006').
  - Workaround: smoke tests and local verification use `db.create_all()` which works for testing purposes.
  - Recommended: review migration `revision` identifiers and `down_revision` values in `migrations/versions` to ensure a linear chain before running in production.

Testing
- Run the smoke verification script locally:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
PYTHONPATH=. python tests/verify_pos.py
```

Beta next steps
- Validate and fix migrations for a clean `alembic` history.
- Add more unit tests and CI coverage for critical flows (payments, refunds, loyalty).
- Harden authentication/authorization and production config for rate-limiting and CSRF.

**Company**
- **Company Name:** Aidni Global LLP
- **Developed By:** Hardik Gajjar
- **Contact Email:** info@aidniglobal.in

© 2025 Aidni Global LLP. All rights reserved.
