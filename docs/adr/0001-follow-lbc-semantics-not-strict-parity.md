# Models follow lbc semantics, not strict parity

vntd's `Ad` and `User` take the Leboncoin client (lbc) as their model: an attribute that exists in both must hold the same kind of data, and a name must describe what it contains. We do not mirror lbc field for field. Fields Vinted has no source for are left out rather than kept as always-`None`, and aliases are added only where the meaning is identical.

## Consequences

- `Ad.status` is the lifecycle of the listing (as in lbc), so the physical state of the item moved to a new `Ad.condition`. This changes what `status` returns, which is why it ships as 1.3.0.
- Names that look alike but differ in meaning are deliberately not aliased: `total_ads` (lbc: items on sale; Vinted's `total_items_count` includes sold ones) and `category_name` (lbc: top-level category; Vinted: leaf category).
- `User.id` stays an `int`, `attributes` is not added, and `presence` is not added.
