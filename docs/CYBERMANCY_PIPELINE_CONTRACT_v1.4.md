# Cybermancy Adversary & Environment Pipeline Contract v1.4

**Source-shape target:** Cybermancy v0.2.0's qualified Foundry 14.368 / Daggerheart 2.10.5 combination. **Live generator-import qualification:** pending.

The design, mechanics approval gate, Fast Play, visual, PDF, and package requirements from `history/CYBERMANCY_PIPELINE_CONTRACT_v1.2.md` remain in force. This document supersedes only its Foundry implementation target and asset-path rules. Entity Spec v1.1 remains the creative source schema. Package Builder v1.4.0 is the current compiler.

## Foundry projection

- Adversary standard attack: `system.attack.damage.main` for hit point damage and `system.attack.damage.resources` for auxiliary resource damage. The canonical spec currently encodes only a main attack. The approved `customFormula` compiles to `damage.main.value.custom`.
- Features: separate embedded `feature` Items on both Adversary and Environment Actors. Feature form and actions are generated from approved rules text. Text-only actions do not imply automated damage, costs, statuses, or saves.
- Environments: `system.impulses` is a string; potential adversaries are keyed groups of verified Actor UUIDs. Unresolved names remain in GM notes and flags. Do not invent or publish world-specific `Actor.*` references as portable compendium links.
- Adversary Horde: Entity Spec v1.1 lacks a `hordeDamage` field required for Daggerheart 2 `typeData`. Builder v1.4.0 fails Horde builds until that canonical mechanic is specified and compiled; it must not silently assume a formula.
- Runtime art paths are `modules/cybermancy/assets/images/adversaries/<slug>.png`, `modules/cybermancy/assets/tokens/adversaries/<slug>-token.png`, and `modules/cybermancy/assets/images/environments/<slug>.png`. Source files belong under the Cybermancy repository's `assets/` tree.
- Module source destinations, once a publishing adapter is implemented, are `src/packs/adventures/adversaries/` and `src/packs/adventures/environments/`. The generator's individual ZIP output alone is not a Cybermancy module release.
- World Actor folder IDs are optional import configuration, never fixed production identity. Foundry-generated `_stats` should be left to Foundry. `_key` is retained in export-style JSON for source-pack compatibility.

## Identity and provenance

A new entity may receive deterministic IDs. Before replacing an entity already present in the Cybermancy module, obtain its existing Actor ID, embedded feature IDs, and action IDs from `src/packs`; preserve them or stop for an explicit remapping decision. Existing Cascade Burrowtail and Cascadia Mountain Valley IDs differ from the current generator's deterministic IDs. Renaming a feature must not silently produce a replacement Item. The publishing adapter must check slug/name collisions and stable IDs before proposing changes.

The Feature Library v1 is an authoring reference. It is not raw Daggerheart 2 import data. Do not silently copy official/reference features into Cybermancy without source and usage review. Canonical gameplay mechanics should remain separate from Foundry's versioned projection.

## Acceptance

Run the eight offline fixtures and build both Cascade Burrowtail and Cascadia Mountain Valley packages with actual artwork. Compare generated structure to the Daggerheart 2.10.5 data models and existing Cybermancy source Actors. In a disposable Foundry 14.368 / Daggerheart 2.10.5 world, import, reopen, use actions, re-export, and inspect validation failures and asset paths. Check the Cybermancy release gates after source-pack integration. Offline tests do not establish live runtime compatibility. See `LIVE_VALIDATION.md`.
