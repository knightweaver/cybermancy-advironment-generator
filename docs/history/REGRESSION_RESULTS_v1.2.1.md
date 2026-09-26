# Fast Play v1 Regression Results

**Status:** PASS  
**Date:** 2026-08-16  
**Package Builder:** 1.2.1

All eight locked Fast Play entities were rebuilt with their actual production artwork and regression-rendered through Package Builder v1.2.1.

| Entity | Status | Fast Play | PDF |
|---|---:|---:|---:|
| Abraxas Cult Leader | PASS | 103 words | 1 page |
| Abraxas ritual cave | PASS | 110 words | 2 pages |
| Altered Coyote | PASS | 107 words | 1 page |
| Altered Threshold Cougar | PASS | 110 words | 1 page |
| Cascade Burrowtail | PASS | 87 words | 1 page |
| Cascadia Mountain Valley | PASS | 110 words | 2 pages |
| Cavelor Finn | PASS | 108 words | 1 page |
| Clevermask | PASS | 101 words | 2 pages |

Automated and rendered checks passed:

- Entity Spec v1.1 schema validation and exact Fast Play `featureRefs` resolution.
- Foundry adversary/environment compilation and cross-artifact Fast Play consistency.
- Cascade Burrowtail flat 3 damage custom formula compilation.
- Approved Altered Threshold Cougar Vulnerable + Silenced duration clarification.
- Fast Play precedes Features in every rendered reference.
- All rendered text remains at or above the 10 pt minimum.
- No text crosses horizontal or footer safe areas.
- Explicit measured spacing before `MOTIVES & TACTICS`.
- `EXPERIENCE` label and first value line share the same baseline.
- Attack summary uses a collision-safe one-line/two-line layout without font shrinking.
- Environment Impulses and Potential Adversaries boxes are content-aware.
- Adversary left-column overflow and two-page continuation limits are validated.
- PDF preflight passed for all eight actual-art regression outputs.

Page counts are expected layout outcomes, not errors: compact entities remain one page; content-dense entities may use a second Features page rather than reducing text below 10 pt.
