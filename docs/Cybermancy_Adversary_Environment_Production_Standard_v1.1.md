> **Foundry 14.368 / Daggerheart 2.10.5 implementation:** This design standard remains valid. Use `CYBERMANCY_PIPELINE_CONTRACT_v1.4.md` and Package Builder v1.4.0 for compiled data. Historical 13 / 1.2 target labels below describe the original validation, not the current build target.

# Cybermancy Adversary & Environment Production Standard v1.1

**Status:** NORMATIVE DESIGN STANDARD  
**Target:** Foundry VTT 13.351 / Daggerheart 1.2.7  
**Works with:** Feature Library v1.0.0, Design Front-End v1.1, Entity Spec v1.1, Package Builder v1.2.1

## 1. Purpose

This standard governs how Cybermancy adversaries and environments are designed before deterministic compilation. It preserves Daggerheart mechanical behavior, Cybermancy setting identity, and at-the-table usability.

The production goal is not merely a legal stat block. Every entity should have a clear encounter purpose, an identifiable play loop, and enough tactical or dramatic identity that the GM can run it without reconstructing the design intent during play.

## 2. Authority hierarchy

Use sources in this order:

1. Official Daggerheart adversaries, environments, and features for balance and rules-language precedent.
2. Gold-standard Cybermancy adversaries and environments for setting-specific precedent.
3. Current Cybermancy Foundry exports for implementation/schema precedent.
4. Cybermancy Feature Library v1 for reusable mechanical patterns.

Search first; invent second. Do not mechanically average all Cybermancy Actors.

## 3. Entity design sequence

For each adversary or environment:

1. Define encounter purpose.
2. Resolve Tier and Role / Environment Type.
3. Retrieve comparators.
4. Identify the intended behavior or scene loop.
5. Select/adapt features that express that loop.
6. Check role-defining expectations.
7. Write concise canonical mechanics.
8. Author Fast Play v1 from the approved mechanics and encounter purpose.
9. Review state transitions and edge cases.
10. Present mechanics + Fast Play for user approval before package generation.

## 4. Adversary design expectations

An adversary should normally contain:

- clear Tier and Daggerheart Role;
- Difficulty, thresholds, HP, Stress, attack, experiences, and features appropriate to its role;
- `encounterPurpose` explaining why it exists in the encounter;
- `motivesAndTactics` describing its fiction-first behavior;
- at least one mechanic that expresses the entity's signature identity or forces a meaningful player response;
- coherent action economy for the intended group composition.

Role behavior remains authoritative. A Solo does not have to stand and trade attacks; a Leader does not have to personally attack when commanding allies is more characteristic; a Social adversary may avoid combat entirely.

## 5. Environment design expectations

An environment should normally contain:

- Tier and Environment Type;
- Difficulty;
- impulses;
- potential adversaries where relevant;
- features that produce exploration, traversal, social, or event pressure;
- a scene progression or decision structure that makes the location mechanically distinct.

Environments are not required to be hostile. Restorative, investigative, social, and foreshadowing environments are valid when their mechanics support the adventure purpose.

## 6. Fast Play v1

Fast Play is a **GM-only decision aid**. It compresses design intent into immediate operating guidance.

### 6.1 Design principle

**Dramatic and intended tactical behavior outranks mathematically optimal tactics.**

Fast Play answers:

> What should this entity usually do next, and what important situation should change that choice?

It does not replace the feature text and does not create new rules.

### 6.2 Structure

Each entity has:

- **2-5 ordered prompts**, each with a dynamic label and concise instruction;
- exactly one mandatory **Goal**;
- no more than six rendered entries total including Goal;
- a target of approximately **60-110 words**.

Labels are chosen for the entity rather than forced into a universal template. Examples include:

- Opening
- Default
- Pressure
- Reset
- Reposition
- If Friendly
- If Threatened
- On HP Marked
- On PC Fear
- Spend Fear
- Transition
- Remember

### 6.3 Goal

Goal is mandatory. It describes what successful portrayal should feel like and prevents Fast Play from becoming a pure DPR/optimization guide.

### 6.4 Mechanics duplication

Repeat a number or rule fragment only when the GM needs that information to make or execute the immediate decision without reopening the feature. Otherwise reference the feature by name.

### 6.5 Feature references

Each Fast Play prompt stores non-rendered `featureRefs` containing exact canonical feature names used by that instruction. These references support validation and staleness detection.

A prompt based only on motives, the standard attack, or fiction may use an empty array.

## 7. State-transition completeness

Fast Play authoring doubles as a mechanical QA pass.

Whenever a feature creates a condition, countdown, ongoing effect, attachment, forced state, or persistent modifier, verify that the canonical feature text clearly specifies:

- trigger;
- effect;
- progression or duration;
- how/when it clears;
- any cost required to clear it.

If this cannot be determined, flag the underlying mechanic for review. Do not silently repair the ambiguity inside Fast Play.

## 8. Mechanical writing

Preserve exactly:

- triggers;
- costs;
- ranges;
- targets;
- Difficulty values;
- Reaction traits;
- damage dice/formulas;
- conditions;
- durations;
- movement;
- Fear/Stress expenditure;
- countdown behavior;
- exceptions and limitations.

Remove redundant explanation and decorative prose from mechanical clauses when it impedes scanning.

## 9. Approval gate

Before Package Builder, show the user:

- Tier + Role/Type;
- encounter purpose;
- core statistics;
- complete feature set;
- proposed Fast Play;
- any state-transition ambiguity or rules clarification that requires approval.

Once approved, Fast Play becomes canonical GM-facing data alongside the mechanics.

## 10. Production acceptance

A design is ready for deterministic production when:

- mechanical benchmark review passes;
- intended play loop is clear;
- role/type identity is preserved;
- Fast Play gives an immediate next-action decision path;
- Fast Play references only existing mechanics;
- state transitions are complete;
- the user has approved the proposal.
