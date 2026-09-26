# CYBERMANCY ADVERSARY & ENVIRONMENT PIPELINE CONTRACT

**Version:** 1.2  
**Status:** NORMATIVE  
**Validated target:** Foundry VTT 13.351 / Daggerheart 1.2.7  
**Production components:** Production Standard v1.1 / Feature Library v1 / Design Front-End v1.1 / Entity Spec v1.1 / Package Builder v1.2.2

## 1. Purpose and precedence

This file defines the exact runtime contract for Cybermancy `BUILD ADVERSARY` and `BUILD ENVIRONMENT` requests.

For those requests, this contract is authoritative for:

- workflow;
- canonical schema behavior;
- Fast Play behavior and presentation;
- filename stubs;
- package directory structure;
- Foundry asset paths;
- art formats;
- PDF layout;
- validation;
- output presentation.

Do not silently substitute older Cybermancy conventions, generic Daggerheart layouts, ad-hoc filenames, alternative asset directories, or the broader narrative/editorial "Cybermancy layout."

Explicit current user decisions override this contract. Otherwise, this contract supersedes Pipeline Contract v1.1 on implementation details.

If Foundry VTT or Daggerheart is later upgraded, preserve the creative/mechanical behavior and canonical spec where possible; migrate only the implementation/compiler layer required by the new software version.

---

## 2. Invocation

Recognize either compact command as invoking this pipeline:

```text
BUILD ADVERSARY
Name: <name>
Tier: <1-4>
Role: <Solo|Leader|Bruiser|Standard|Minion|Horde|Ranged|Skulk|Support|Social>
Concept: <1-3 sentences>
```

```text
BUILD ENVIRONMENT
Name: <name>
Tier: <1-4>
Type: <Exploration|Traversal|Social|Event>
Concept: <1-3 sentences>
```

Tier, Role, or Type may be inferred if omitted. Do not ask a clarifying question when the missing value can be reasonably inferred and surfaced as an assumption.

---

## 3. Required workflow

Use this sequence:

```text
IDEATE / BUILD brief
-> normalize concept and assumptions
-> resolve Tier + Role / Environment Type
-> retrieve official Daggerheart comparators
-> retrieve relevant Cybermancy comparators
-> search Feature Library
-> adapt/reuse mechanics where appropriate
-> identify intended dramatic/tactical play loop
-> author proposed Fast Play v1
-> propose concise mechanical stat block + Fast Play
-> USER APPROVAL GATE
-> author canonical <slug>.spec.json (v1.1)
-> Front-End v1.1 review, including Fast Play/state-transition QA
-> generate or reuse approved art assets
-> Package Builder v1.2.2
-> six-gate validation
-> render and visually inspect PDF
-> deliver package and individual convenience files
```

Unless the user explicitly says to skip review, do not run package generation before the proposed mechanics and Fast Play have been shown and approved.

---

## 4. Design authority hierarchy

Use sources in this order:

1. **Official Daggerheart adversaries, environments, and adversary features**
   - mechanical balance authority;
   - Tier/Role precedent;
   - Daggerheart rules-language precedent.
2. **Gold-standard Cybermancy adversaries/environments**
   - Sewerjaw Gator;
   - Liminal Research Drone;
   - Pierjaw Crab;
   - Raz Eels;
   - Mireborn Thralls;
   - Bella;
   - Seattle Underflow Grid for environment behavior.
3. **Current Cybermancy Foundry exports**
   - implementation/schema authority;
   - naming/path precedent;
   - not all Actors are equal balancing precedents.
4. **Cybermancy Feature Library v1**
   - reusable setting-specific mechanical precedent.

Do not mechanically average all Cybermancy Actors.

---

## 5. Feature-selection rule

Search first; invent second.

Preference order:

1. Official Daggerheart feature matching intended Role.
2. Official Daggerheart feature from a mechanically adjacent Role.
3. Embedded feature from a gold-standard Cybermancy adversary.
4. Explicit Cybermancy adversary feature.
5. Cybermancy Device/ICE feature when the concept is technological/networked.
6. New/adapted feature only when existing patterns do not adequately express the desired behavior.

When adapting a feature:

- preserve mechanical purpose;
- rewrite creature-specific wording;
- tune damage/range/cost to Tier and Role;
- explain the comparator/adaptation in the proposal.

Treat reusable families such as Relentless, Minion, Horde, Group Attack, and Momentum as parameterized templates rather than unrelated one-offs.

Cybermancy Class/Subclass features are excluded from adversary generation by default.

---

## 6. Fast Play v1

Fast Play is **GM-facing only** and is canonical for both adversaries and environments.

### 6.1 Purpose

Fast Play tells the GM **what to choose and when**. The full feature text remains authoritative for exact execution.

**Dramatic and intended tactical behavior outranks mathematically optimal tactics.**

### 6.2 Structure

```json
"fastPlay": {
  "prompts": [
    {
      "label": "Opening",
      "text": "...",
      "featureRefs": ["Existing Feature Name"]
    }
  ],
  "goal": "..."
}
```

Rules:

- 2-5 ordered prompts;
- exactly one mandatory Goal;
- dynamic prompt labels rather than fixed categories;
- no more than six rendered entries including Goal;
- approximately 60-110 words total;
- `featureRefs` are non-rendered metadata and must exactly match canonical feature names;
- prompts based on motives, the standard attack, or fiction may use an empty `featureRefs` array;
- repeat a mechanical value only when needed for immediate decision-making;
- never invent a new rule inside Fast Play.

### 6.3 State-transition QA

If Fast Play authoring exposes an ambiguous condition, countdown, duration, clearing rule, attachment state, or other ongoing effect, flag and fix the **underlying feature** before packaging. Do not repair the ambiguity only in Fast Play.

### 6.4 Presentation order

GM-facing reference order:

1. identity / Tier / Role or Type;
2. description;
3. motives/impulses and core statistics;
4. **FAST PLAY**;
5. full **FEATURES**.

Fast Play appears in Foundry and the printable reference. It is not player-facing.

---

## 7. Canonical specification

The canonical `.spec.json` is the editable source of truth.

Exact source filename:

```text
<slug>.spec.json
```

Spec v1.1 must validate against:

```text
cybermancy-entity-spec-v1.1.schema.json
```

with:

```json
"specVersion": "1.1"
```

The canonical spec remains independent of deployment-only implementation details wherever practical. Generated Foundry IDs, `_key` values, package boilerplate, and similar compiler concerns belong in Package Builder.

The canonical print node remains:

```json
{
  "pageTarget": 1,
  "style": "cybermancy-daggerheart-reference",
  "includeArt": true
}
```

Spec v1.1 additionally permits optional `mechanics.attack.damage.customFormula` for approved flat/nonstandard attack formulas. When present, it is authoritative for compiled Foundry damage and print display.

---

## 8. Slug and naming invariants

Use lowercase kebab-case derived from the approved entity name.

Example:

```text
Abraxas modified Deer -> abraxas-modified-deer
```

Do not add arbitrary prefixes such as `cybermancy-`, `actor-`, `adversary-`, or `environment-` unless part of the actual name.

### Package root

```text
<slug>-package/
```

### Package ZIP

```text
<slug>-package.zip
```

---

## 9. Exact Package Builder v1.2.2 package structure

### Adversary

```text
<slug>-package.zip
└── <slug>-package/
    ├── manifest.json
    ├── validation.json
    ├── source/
    │   ├── <slug>.spec.json
    │   ├── <slug>.art-briefs.json
    │   ├── <slug>.print-model.json
    │   └── schema/
    │       └── cybermancy-entity-spec-v1.1.schema.json
    ├── foundry/
    │   └── <slug>.json
    ├── assets/
    │   ├── images/adversaries/<slug>.png
    │   └── tokens/adversaries/<slug>-token.png
    └── print/
        └── <slug>.pdf
```

### Environment

```text
<slug>-package.zip
└── <slug>-package/
    ├── manifest.json
    ├── validation.json
    ├── source/
    │   ├── <slug>.spec.json
    │   ├── <slug>.art-briefs.json
    │   ├── <slug>.print-model.json
    │   └── schema/
    │       └── cybermancy-entity-spec-v1.1.schema.json
    ├── foundry/
    │   └── <slug>.json
    ├── assets/images/environments/<slug>.png
    └── print/<slug>.pdf
```

These internal paths are normative.

### User-facing convenience files

```text
<slug>.json
<slug>.png
<slug>-token.png          # adversary only
<slug>.spec.json
<slug>-reference.pdf
```

The convenience PDF name does not change the authoritative package location `print/<slug>.pdf`.

---

## 10. Foundry asset-path invariants

Canonical/Foundry paths must be exactly:

```text
worlds/cybermancer/assets/images/adversaries/<slug>.png
worlds/cybermancer/assets/tokens/adversaries/<slug>-token.png
worlds/cybermancer/assets/images/environments/<slug>.png
```

Do not substitute:

- `modules/cybermancy/...`;
- `worlds/cybermancy/...`;
- package-local `assets/...` paths;
- singular `adversary/` or `environment/` directories.

The world token is **`cybermancer`**.

Fast Play is compiled into GM-visible Foundry description content and retained structurally at:

```text
flags.cybermancy.fastPlay
```

for future sheet/UI support and staleness validation.

---

## 11. Current Foundry target configuration

```text
Foundry VTT: 13.351
Daggerheart: 1.2.7
Adversary Folder ID:   37VSZjNUFnmscbRN
Environment Folder ID: KPCXQgkywXC3THMB
```

Deployment-specific IDs belong in configuration rather than canonical gameplay design.

The compiler generates coherent deterministic 16-character Foundry IDs and valid `_key` relationships for adversary Actors and embedded feature Items.

---

## 12. Artwork contract

### Shared art direction

All adversary portraits, adversary tokens, and environment images should follow the same global rendering goals:

- gritty Cybermancy semi-photorealism;
- strong focal clarity and subject separation;
- richer, more vibrant color accents than the earlier muddy/dark token baseline;
- readable midtone contrast that remains legible in print and at VTT scale;
- preserve atmosphere without burying the subject or location in low-contrast shadow;
- no text, labels, stat blocks, or UI unless explicitly requested elsewhere.

### Adversary portrait

Default:

- 4:5 aspect ratio;
- cinematic/semi-photorealistic;
- believable biological/human/technological subject first;
- Cybermancy corruption/cybernetics/Resonance/ritual details second;
- strong readable silhouette;
- atmospheric environment;
- vivid-but-controlled palette with stronger contrast and clearer focal lighting;
- no text, labels, stat block, or UI.

### Adversary token

Default:

- 1:1 square PNG;
- 1254 x 1254 reference size;
- same identity as portrait;
- tight face/body composition readable at token scale;
- thick distressed dark-metal circular rim nearly touching square edges;
- all artwork contained cleanly inside the ring;
- everything outside the outer token ring fully transparent;
- vibrant, high-clarity palette with strong readable contrast;
- no text, labels, or logos.

Transparent-background output is the normative default for token generation. Opaque black corner fill is superseded and should not be used for new builds.

Approved token precedents remain Sewerjaw Gator, Liminal Research Drone, and the transparent-background Cascade Burrowtail revision.

### Environment art

Default:

- 3:2 landscape;
- cinematic/semi-photorealistic establishing image;
- rich, readable atmospheric palette with clearer shape separation and stronger accent lighting where appropriate;
- no text, labels, UI, or stat block.

---

## 13. PDF contract - Package Builder v1.2.2

The PDF renderer is the Daggerheart-inspired compact GM-reference renderer, **not** the narrative Cybermancy layout.

Canonical style identifier:

```text
cybermancy-daggerheart-reference
```

### Page geometry

- US Letter portrait, 612 x 792 pt;
- approximately 42 pt margins;
- two-column-capable grammar;
- approximately 12-14 pt column gap;
- print-friendly warm paper background.

### Visual grammar

Preserve:

- dense Daggerheart-inspired rulebook presentation;
- rounded warm-cream cards;
- thin warm-gold/tan borders;
- bold entity name;
- Tier + Role/Type directly below;
- short italic/compact description;
- Motives & Tactics for adversaries;
- Impulses and Potential Adversaries for environments, with content-aware box heights;
- adversary quick stats including Difficulty / Thresholds / HP / Stress;
- attack / weapon / range / damage, using a collision-safe wrap rather than shrinking below 10 pt;
- Experience rendered as a measured label/value row with first-line baseline alignment;
- measured section spacing between description, Motives & Tactics, motives text, and core stats;
- **FAST PLAY before FEATURES**;
- Fast Play labels in **bold italic**, description text regular;
- Feature Name bold and Feature Type **bold italic**;
- costs/dice emphasized where helpful for rapid scanning;
- named conditions visually distinguishable through typography/wording rather than clutter;
- artwork separate from mechanics;
- stat-block density takes precedence over illustration size.

### Typography

- **10 pt minimum for body, stat, feature, and Fast Play text**;
- headings larger as appropriate;
- do not solve page pressure by shrinking below 10 pt.

### Pagination

- one page is the target when readable;
- portrait placement may adapt to unused column space to preserve one-page readability;
- use a second page when complete mechanics cannot fit at 10 pt;
- entity references support a maximum of two pages by default.

### Footer

```text
CYBERMANCY // GM REFERENCE
```

Do not substitute a magazine spread, dark chapter opener, generic Markdown-to-PDF page, or decorative monster card.

---

## 14. Validation contract

A completed build must pass six conceptual gates:

1. **Canonical spec/schema validity**
   - v1.1 schema passes;
   - Fast Play has 2-5 prompts + Goal;
   - all `featureRefs` resolve exactly;
   - canonical Foundry paths are valid.
2. **Mechanical benchmark / behavior sanity**
   - Tier/Role/Type fit;
   - intended behavior aligns with encounter purpose and motives/impulses;
   - state-transition completeness reviewed.
3. **Foundry JSON / compiled structure**
   - output parses;
   - core stats match spec;
   - feature names/order match;
   - Fast Play is present in description and flags;
   - custom damage formula, when used, compiles correctly;
   - adversary IDs/relationships are coherent.
4. **Cross-artifact consistency**
   - Fast Play matches across spec, print model, Foundry, and PDF;
   - mechanics remain consistent across artifacts.
5. **Art QA**
   - files exist and open;
   - subject identity is consistent;
   - portrait/token/environment dimensions and aspect ratios are checked against defaults;
   - adversary token PNGs must preserve an alpha channel;
   - pixels outside the outer token ring must be transparent rather than opaque black fill;
   - art readability is reviewed for excessively dark or muddy output, with low-contrast results flagged for editorial regeneration.
6. **PDF QA**
   - PDF opens;
   - Fast Play and Features are present;
   - 1-2 pages;
   - no clipping, overlap, broken glyphs, or unreadable layout on render inspection;
   - body/stat/Fast Play text remains at least 10 pt;
   - rendered-PDF geometry remains inside printable horizontal and footer safe areas;
   - adversary left-column content does not overflow its card;
   - environment summary and potential-adversary boxes expand to measured content rather than clipping.

Fast Play outside the 60-110 word target is an editorial warning, not an automatic gameplay rewrite.

---

## 15. Regression and acceptance references

Retain original implementation precedents:

### Sewerjaw Gator

- Package Builder regression fixture;
- Foundry JSON previously confirmed to import;
- approved token reference.

### Cascadia Mountain Valley

- primary environment image readability/color-balance regression reference for the brighter, clearer art baseline.

### Seattle Underflow Grid

- Environment compilation/PDF precedent.

### Abraxas Modified Deer

- accepted full end-to-end BUILD ADVERSARY precedent.

Fast Play v1 adds eight locked regression fixtures spanning varied behaviors:

- Cascade Burrowtail - Minion / trigger chain;
- Clevermask - Social / behavior and relationship state;
- Altered Coyote - Standard / formation tactics;
- Altered Threshold Cougar - Skulk / ambush-reset loop;
- Cavelor Finn - Solo / ambush-disengage behavior;
- Abraxas Cult Leader - Leader / competing action priorities;
- Cascadia Mountain Valley - Exploration / scene progression;
- Abraxas Ritual Cave - Event / multi-objective pressure.

Cascade Burrowtail is the primary packaged Fast Play regression. Cascadia Mountain Valley is the primary environment renderer regression.

---

## 16. Delivery behavior

After Package Builder completes, provide:

1. complete `<slug>-package.zip`;
2. Foundry `<slug>.json`;
3. individual portrait/environment art;
4. adversary token art when applicable;
5. `<slug>-reference.pdf`;
6. canonical `<slug>.spec.json`.

State validation status and identify any intentional migration from the validated implementation target.

Do not rename or relocate artifacts ad hoc.

---

## 17. Compute guidance

Default to Medium reasoning/compute for routine pipeline use.

Use High when:

- mechanics are unusually novel;
- a Solo/Leader has complex action economy;
- an Environment has interacting subsystems;
- several adversaries work as a coordinated mechanical family;
- Fast Play exposes ambiguous state transitions;
- the pipeline/compiler itself is being changed or debugged.
