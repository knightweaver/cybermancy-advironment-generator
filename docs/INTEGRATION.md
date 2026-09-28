# Cybermancy module integration boundary

This repository owns authoring standards and deterministic compilation. The Cybermancy repository owns approved source specifications, art, `src/packs` entries, and releases. Do not write LevelDB `packs/` directly; Cybermancy's `npm run compile:packs` builds those from `src/packs`.

Publication workflow and checks:

1. Read the target repository and compare the proposed slug/name against existing Actor sources. Preserve current Actor and embedded Item/action IDs for revisions, including Cascade Burrowtail and Cascadia Mountain Valley. Refuse ambiguous identity matches.
2. Read canonical approved specifications and real art files; compile deterministic Actor JSON. Write art under Cybermancy `assets/` and use `modules/cybermancy/assets/...` references.
3. Resolve environment adversary names to verified `Compendium.cybermancy.cybermancy-adversaries.Actor.<id>` UUIDs. Preserve any unresolved names as visible text and report them. Never convert a world `Actor.<id>` to a compendium UUID by guessing.
4. Stage new JSON in the correct `src/packs/adventures/{adversaries,environments}` family, preserving Tier Folder records. Revisions of existing actors require explicit ID reconciliation and are not supported by the additive adapter.
5. Run Cybermancy's module/release checks: `validate:assets -- --strict-prefix`, `validate:release`, `compile:packs`, and `validate:compiled-packs`. Propose a PR containing the approved spec, source JSON, art, provenance, and validation report. Publication follows Cybermancy's own module release workflow.

**Rulebook publication is separate and optional.** Adding or revising module adversaries/environments does not require a rulebook inventory refresh, publication-manifest/freeze update, normalized-corpus rebuild, or PDF rebuild. Do not include rulebook inventory, manifest, freeze, or rendered-publication changes in an ordinary module-content PR. Run the rulebook maintenance/publication workflow only when intentionally publishing those content changes into the rulebook as a separate task.

Existing module source is authoritative for published IDs. The additive adapter below refuses collisions rather than silently replacing Actors.

## Additive publication adapter

`src/publish_to_cybermancy.py` stages approved **new** packages into a checked-out Cybermancy module. It dry-runs by default; pass `--write` to copy after all packages pass preflight.

```bash
python src/publish_to_cybermancy.py --cybermancy-repo ../cybermancy \
  --package build/cascadian-first-peoples-hunter-package \
  --package build/ballard-reach-floating-commons-package
python src/publish_to_cybermancy.py --cybermancy-repo ../cybermancy \
  --package build/cascadian-first-peoples-hunter-package \
  --package build/ballard-reach-floating-commons-package --write
```

The adapter checks all six package gates, spec approval, Actor name/ID collisions, Tier folder records, embedded IDs/keys, art paths, and destination occupancy. It stages Actor sources, canonical art, specs, and validation reports; reference PDFs can be regenerated from the approved specs and art and are not copied into the module. Re-running on existing Actors fails. It neither edits `packs/` nor updates release/rulebook manifests. After staging, run only the module/release checks above unless a separate rulebook-publication task has been explicitly requested. Preserve the historical v0.2.0 migration baseline.
