# Repository instructions

- For `BUILD ADVERSARY` and `BUILD ENVIRONMENT`, read `docs/CYBERMANCY_PIPELINE_CONTRACT_v1.4.md`, then the design and front-end standards. Preserve the approval gate for mechanics and Fast Play before generating a package.
- Treat `schema/cybermancy-entity-spec-v1.1.schema.json` and approved specs as creative source. `src/package_builder.py` is the Foundry 14.368 / Daggerheart 2.10.5 implementation. Do not derive target shapes from superseded `docs/history/` files.
- Run `python tests/test_pipeline.py` after compiler, fixture, or renderer changes. Update source-shape evidence and target checks when changing Foundry or Daggerheart versions.
- For Cybermancy module publication, follow `docs/INTEGRATION.md`. The additive adapter stages approved new packages into a local checkout; existing module source preserves published Actor, Item, and action IDs. It does not prove live Foundry import.
- Do not copy Feature Library source text, secrets, or production art into this public repository without confirming provenance and redistribution rights.
