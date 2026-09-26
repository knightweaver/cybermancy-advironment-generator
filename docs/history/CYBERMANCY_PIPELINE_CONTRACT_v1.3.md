# Cybermancy Adversary & Environment Pipeline Contract v1.3

**Target tested against source:** Foundry VTT 14.360 / Foundryborne Daggerheart 2.1.2. **Live-world import validation remains pending.**

This is the v1.2 contract plus the implementation amendments below. All unmodified creative, Fast Play, art, naming, package, PDF, approval, and validation requirements in `archive/CYBERMANCY_PIPELINE_CONTRACT_v1.2.md` remain normative. The Entity Spec remains v1.1; the implementation compiler is Package Builder v1.3.0. No mechanical rebalance is implied.

## Foundry 14 / Daggerheart 2.1 implementation amendments

1. The standard adversary attack uses `system.attack.damage.parts.hitPoints`, a keyed object rather than an array. Preserve canonical attack damage, including `customFormula`.
2. Environment features compile as embedded `feature` Items in `items`, with deterministic IDs, `system.description`, `system.actions`, and `system.featureForm`. There is no `system.features` output. Adversary features remain embedded Items.
3. `system.potentialAdversaries` is a keyed group containing verified Actor UUIDs. Canonical names without verified UUIDs remain in `flags.cybermancy.potentialAdversaryNames` and GM-visible `system.notes`; they are not fabricated as links. Supply an exact-name-to-UUID JSON map at build time to link them.
4. Environment `system.impulses` is a string and `system.description` and `system.notes` are HTML. The canonical spec retains its arrays and prose; compilation performs this mapping.
5. Newly emitted Actors omit forged `_stats`. Foundry stamps document metadata on import. `_key` and deterministic `_id` fields remain for package/export compatibility; the import adapter should ignore `_key` when using `Actor.create` if Foundry does not accept it.
6. Folder IDs are target-world configuration, not fixed constants. The builder defaults to no folder and accepts explicit verified IDs. An importing macro must resolve folders in the destination world and report missing ones rather than silently using 13.x IDs.
7. The v1.2 canonical asset paths under `worlds/cybermancer/assets/` remain unchanged until the upgraded-world file browser confirms a different deployment root. If changed, update the spec paths, path validator, contract, deployment copy destination, and import test together.
8. Source specs for this target record the actual installed 14.x and 2.1.x patch versions. The provided fixtures use 14.360 / 2.1.2; adjust them to the installed versions before claiming live validation. The Feature Library v1 implementation blueprints are design references, not raw 2.1 import data.

## Required live acceptance

Rebuild Cascade Burrowtail and Cascadia Mountain Valley. In a disposable upgraded world, import and reopen both; verify attack roll/damage including custom formula, feature visibility and action use, Fast Play, token/portrait/environment art, folder placement, and no validation errors. Export the resulting Actors and compare core mechanics and feature text to the canonical specs. Run the adventure batch importer twice and verify imported/skipped/error counts and no duplicates. Record the exact Foundry and Daggerheart patch versions, art root, folder IDs, import method, and re-export results. Offline fixture tests alone do not establish live compatibility.
