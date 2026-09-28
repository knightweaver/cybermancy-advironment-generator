# Cybermancy Adversary & Environment Generator

Repository source for the Cybermancy adversary/environment authoring pipeline. Version 1.4.0 targets the **source shape** qualified by Cybermancy v0.2.0: Foundry VTT **14.368** and Foundryborne Daggerheart **2.10.5**. Runtime import of output from this generator remains to be qualified in a disposable world.

## Normal workflow

1. Describe the entity, Tier, Role/Type, and encounter purpose.
2. Consult current Daggerheart and Cybermancy comparators and Feature Library v1. Present mechanics and Fast Play for approval under `docs/CYBERMANCY_PIPELINE_CONTRACT_v1.4.md`.
3. Author the approved Entity Spec v1.1 and supply production portrait/token or environment art.
4. Validate and build with the commands below; review the PDF and `validation.json`.
5. Follow `docs/LIVE_VALIDATION.md` before accepting runtime compatibility. For eventual module publication, use the identity and release boundary in `docs/INTEGRATION.md`.

Approved new entities can be staged into a Cybermancy checkout using `src/publish_to_cybermancy.py`. It refuses changes to previously published Actors until their IDs are explicitly reconciled.

```bash
python -m pip install -r requirements.txt
python tests/test_pipeline.py
python src/package_builder.py validate --spec tests/fixtures/cascade-burrowtail.spec.json --schema schema/cybermancy-entity-spec-v1.1.schema.json
python src/package_builder.py build --spec tests/fixtures/cascade-burrowtail.spec.json --schema schema/cybermancy-entity-spec-v1.1.schema.json --output-dir build --portrait portrait.png --token token.png --zip-output build/cascade-burrowtail-package.zip
python src/package_builder.py build --spec tests/fixtures/cascadia-mountain-valley.spec.json --schema schema/cybermancy-entity-spec-v1.1.schema.json --output-dir build --environment-art environment.png --zip-output build/cascadia-mountain-valley-package.zip
```

The sample commands require your real artwork. Generated test art is never used for publication. `--adversary-uuids` can provide a JSON mapping of exact environment adversary names to verified Actor UUIDs. Art paths in specs and output must point at `modules/cybermancy/assets/...`.

## Repository layout

- `src/package_builder.py`: deterministic compiler and PDF renderer.
- `schema/`: canonical creative specification, currently v1.1.
- `tests/fixtures/`: approved regression corpus; `tests/test_pipeline.py`: offline checks.
- `docs/`: current contract, production standard, front-end standard, integration and live validation. `docs/history/` holds superseded 13/1.x and 14/2.1 documents for provenance.
- `fonts/`: PT Sans and PT Sans Narrow with Open Font Licenses.

The Feature Library v1 is a separately maintained authoring reference; the compiler does not require it at runtime. Source content and official Daggerheart text should be reviewed for provenance and redistribution rights before being copied into this public repository.
