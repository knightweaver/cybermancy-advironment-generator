# Cybermancy module integration boundary

This repository owns authoring standards and deterministic compilation. The Cybermancy repository owns approved source specifications, art, `src/packs` entries, and releases. Do not write LevelDB `packs/` directly; Cybermancy's `npm run compile:packs` builds those from `src/packs`.

For a future publication adapter:

1. Read the target repository and compare the proposed slug/name against existing Actor sources. Preserve current Actor and embedded Item/action IDs for revisions, including Cascade Burrowtail and Cascadia Mountain Valley. Refuse ambiguous identity matches.
2. Read canonical approved specifications and real art files; compile deterministic Actor JSON. Write art under Cybermancy `assets/` and use `modules/cybermancy/assets/...` references.
3. Resolve environment adversary names to verified `Compendium.cybermancy.cybermancy-adversaries.Actor.<id>` UUIDs. Preserve any unresolved names as visible text and report them. Never convert a world `Actor.<id>` to a compendium UUID by guessing.
4. Stage new or updated JSON in the correct `src/packs/adventures/{adversaries,environments}` family, preserving the repository's source filename and Folder record conventions.
5. Run Cybermancy's `validate:assets -- --strict-prefix`, `validate:release`, `compile:packs`, `validate:compiled-packs`, and relevant rulebook source checks. Propose a PR containing the approved spec, source JSON, art, provenance, and validation report. Publication follows Cybermancy's own release workflow.

No adapter in this initial repository writes to Cybermancy. Existing module source is authoritative for its published IDs. This boundary prevents a new generator release from silently rewriting previously published Actors.
