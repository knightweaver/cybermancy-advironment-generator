> **Foundry 14.368 / Daggerheart 2.10.5 implementation:** This design standard remains valid. Use `CYBERMANCY_PIPELINE_CONTRACT_v1.4.md` and Package Builder v1.4.0 for compiled data. Historical 13 / 1.2 target labels below describe the original validation, not the current build target.

# Cybermancy Design Front-End Standard v1.1

## Purpose

The front end converts an abbreviated entity idea into the evidence packet needed to author a mechanically grounded canonical specification. It is the boundary between creative ideation and deterministic production.

## Core design principle

Do not invent a complete Daggerheart stat block from memory. Resolve Tier/Role/Environment Type, retrieve official comparators, retrieve Cybermancy comparators, consult Feature Library v1, and only then synthesize mechanics and Fast Play.

## Resolution rules

- Explicit user Tier/Role/Environment Type always wins.
- Missing Tier may be conservatively inferred; low-confidence inference is surfaced.
- Missing Role/Type may be heuristically scored and documented in `design-context.json`.
- IDEATE mode may deliberately vary classifications across candidates.

## Comparator rules

- Adversaries: target at least three official same-Tier/Role records when the corpus supports it, plus one to three Cybermancy comparators.
- Environments: target at least two same-Tier official comparators when available, plus relevant Cybermancy precedents.

## Feature selection

Search Feature Library v1 in source-authority order. Favor role-defining mechanics and a coherent encounter loop. Device/ICE features are excluded unless the fiction is technological/networked. Class/Subclass features remain excluded by default.

## Fast Play authoring

Fast Play is authored **after the mechanical loop is understood and before the approval gate**.

The reasoning author must identify:

1. **Encounter purpose** - what successful portrayal should feel like.
2. **Opening state** - only when setup materially changes play.
3. **Ordinary/default decision** - what to do when no special trigger dominates.
4. **Important decision triggers** - generally 0-3, using dynamic labels.
5. **Easy-to-forget execution detail** - only when genuinely useful.
6. **Goal** - mandatory dramatic/tactical behavior statement.

Do not force labels that do not fit the entity. A Social adversary may use `If Friendly`/`If Threatened`; a Skulk may use `Reset`; an Event environment may use `On PC Fear`/`Spend Fear`.

### Fast Play quality rules

- Dramatic/tactical behavior over mathematical optimization.
- 2-5 prompts + Goal; normally 60-110 words total.
- Repeat mechanics only when needed for immediate decision-making.
- Feature names may be referenced; exact rules stay in Features.
- Every `featureRefs` entry must exactly match a canonical feature name.
- If the reasoning author cannot determine what the entity should normally do next, the mechanical design is not behaviorally complete.
- If a condition/countdown/ongoing effect lacks a clear duration/progression/clear rule, flag the underlying feature; do not patch it only inside Fast Play.

## Approval gate

The proposal shown for approval should include:

- Tier + Role/Type and encounter purpose;
- core stats/mechanics;
- features;
- concise Fast Play block;
- any state-transition ambiguity requiring a rules decision.

## Review gate before Package Builder

1. JSON Schema v1.1 passes.
2. Tier/Role stats outside official observed bands are flagged.
3. Feature-count outliers are flagged.
4. Role-defining mechanics are checked.
5. Comparator-reference minimums are checked.
6. Environment impulse count is checked.
7. Fast Play has 2-5 prompts + Goal.
8. Fast Play goal matches encounter purpose and motives/impulses.
9. Fast Play `featureRefs` resolve exactly.
10. Fast Play duplicates no more mechanics than necessary.
11. State-transition completeness receives explicit reasoning review.
12. Estimated Fast Play word count outside 60-110 is flagged for editorial review.

## Authoring boundary

The deterministic front end retrieves and organizes evidence. A reasoning author writes the canonical spec and Fast Play. Package Builder then compiles approved content deterministically. The compiler must not invent tactical guidance.

## Traceability

Feature Library family/variant provenance remains in design context/review sidecars. Fast Play additionally records `featureRefs` in the canonical spec for exact-name validation and staleness detection.
