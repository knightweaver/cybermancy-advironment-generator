# Cybermancy Package Builder v1.2.1

## Purpose

Package Builder v1.2.1 deterministically compiles an approved Cybermancy Entity Spec v1.1 into Foundry JSON, print model, compact reference PDF, manifest, validation report, and final package ZIP.

## Fast Play baseline introduced in v1.2

- Compiles Fast Play v1 for adversaries **and** environments.
- Preserves structured Fast Play data in `flags.cybermancy.fastPlay`.
- Renders Fast Play before full Features in the PDF.
- Validates exact Fast Play `featureRefs`.
- Validates 2-5 prompts + Goal and warns outside the 60-110 word target.
- Enforces 10 pt minimum PDF body/stat/Fast Play typography.
- Adds optional attack `customFormula` support, resolving the previous flat-damage compatibility workaround.
- Emits schema v1.1 in each package.

## Corrected renderer in v1.2.1

Package Builder v1.2.1 is a layout/QA patch. It does not change Fast Play v1 semantics or the Entity Spec v1.1 schema.

- Replaces the hand-tuned description-to-`MOTIVES & TACTICS` spacing with explicit measured section spacing.
- Renders `EXPERIENCE` as a measured label/value row with a shared first-line baseline.
- Makes the adversary attack summary collision-safe without shrinking below 10 pt; long combinations wrap into a controlled second line.
- Makes environment Impulses and Potential Adversaries boxes content-aware rather than fixed-height.
- Adds adversary left-column overflow detection and two-page continuation limits.
- Adds PDF geometry QA using the rendered PDF: minimum font size, printable bounds, and footer-safe-area checks.
- Expands renderer regression coverage to all eight locked Fast Play v1 test entities.

## CLI

```bash
python src/package_builder.py build \
  --spec path/to/entity.spec.json \
  --schema schema/cybermancy-entity-spec-v1.1.schema.json \
  --output-dir build \
  --portrait path/to/portrait.png \
  --token path/to/token.png
```

Environment builds use `--environment-art` instead of portrait/token.

Use `--zip-output path/to/<slug>-package.zip` to create the final archive.

## Compiler behavior

The compiler does not create or revise gameplay mechanics. It validates and compiles approved spec content. Fast Play text is never synthesized by Package Builder.

### Foundry

Fast Play is appended to GM-facing description HTML and preserved structurally in:

```text
flags.cybermancy.fastPlay
```

Feature items remain separate Foundry features. The standard attack remains the actor attack.

### PDF

Fast Play appears after the entity's identity/core behavioral information and before full Features. Labels use bold italic treatment. Body text is never reduced below 10 pt; if one-page composition cannot remain readable, the renderer uses a second page.

## Validation

The builder writes `validation.json` with six gates. Fast Play-specific failures are schema/consistency errors; editorial length is a warning. PDF rendering is additionally inspected for layout geometry, minimum 10 pt text, printable bounds, and renderer-reported overflow before Gate F can pass.

## Regression target

Release regression covers all eight locked Fast Play v1 fixtures with actual production artwork: Cascade Burrowtail, Clevermask, Altered Coyote, Altered Threshold Cougar, Cavelor Finn, Abraxas Cult Leader, Cascadia Mountain Valley, and Abraxas Ritual Cave.

The automated test suite additionally asserts the two v1.2.1 layout regressions directly: visible separation before `MOTIVES & TACTICS` and first-line baseline alignment for `EXPERIENCE`.
