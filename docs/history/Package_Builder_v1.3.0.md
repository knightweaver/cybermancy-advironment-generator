# Package Builder v1.3.0

**Compilation target:** Foundry 14.x / Foundryborne Daggerheart 2.1.x. The v1.2.2 art requirements remain active; source was available only through v1.2.1, so this release reimplements alpha-channel and outside-ring transparency checks. See the v1.3 Pipeline Contract and README for the outstanding live-world validation.

The approved Entity Spec v1.1 remains the canonical design input. The builder outputs Foundry JSON, print model, compact PDF, validation report, and package ZIP. Attack damage is keyed by `hitPoints`. Adversary and environment features are embedded Items. Environment names without verified Actor UUIDs remain visible but unlinked.

For an environment, an optional JSON map can associate exact canonical names with verified Foundry Actor UUIDs:

```json
{"Altered Raven":"Actor.1234567890abcdef"}
```

Pass it with `--adversary-uuids path/to/verified-uuids.json`. UUIDs must be resolved in the intended world before use. Pass `--adversary-folder-id` or `--environment-folder-id` only after checking those folders in that world; absent arguments place Actors at the root. The builder does not infer or create destination folders.

The `foundry.targetCoreVersion` and `targetSystemVersion` fields are retained in the canonical spec as build target provenance. Update the two fields for the installed 14.x / 2.1.x patch versions without changing the creative mechanics. Do not manually stamp `_stats`.
