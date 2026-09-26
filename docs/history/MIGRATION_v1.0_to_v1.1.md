# Entity Spec v1.0 -> v1.1 Migration

Spec v1.1 adds Fast Play v1 as required canonical GM-facing data. Existing mechanics do not need to be redesigned merely to migrate.

## Required migration

1. Change `specVersion` from `1.0` to `1.1`.
2. Update `$schema` to `cybermancy-entity-spec-v1.1.schema.json`.
3. Author and insert the approved `fastPlay` object.
4. Validate every `featureRefs` entry against exact feature names.
5. Run the state-transition completeness review.
6. Recompile through Package Builder v1.2.1.

## Optional attack migration

Spec v1.1 allows `mechanics.attack.damage.customFormula` for approved attacks whose actual Foundry formula is not represented by the ordinary dice fields. The Cascade Burrowtail uses `customFormula: "3"`, replacing the earlier builder-side workaround while preserving its flat 3 physical damage.

## Important

The migration utility does **not** invent Fast Play. A reasoning author or GM must supply an approved Fast Play JSON object.
