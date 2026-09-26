# Package Builder v1.4.0

The compiler maps approved Entity Spec v1.1 into Foundry 14.368 / Daggerheart 2.10.5 source-shaped Actors, print model, compact reference PDF, validation report, and individual ZIP. Its source shape is checked against the Daggerheart 2.10.5 tag and Cybermancy v0.2.0 migration audit. It has not been imported live into Foundry.

The attack uses `system.attack.damage.main` and `.resources`, the 2.10.5 model. Environment and adversary features are embedded Items. An environment's optional `--adversary-uuids path.json` input maps exact potential-adversary names to verified Actor UUIDs. Unresolved names remain in notes and flags. For module publication, only verified portable Compendium UUIDs should be accepted. Folder-ID arguments are optional and specific to the intended world.

The portrait, token, and environment art paths use `modules/cybermancy/assets/...`. The builder requires an alpha channel and transparent ring exterior for adversary tokens, as required by the v1.2.2 art standard. Six bundled PT Sans fonts and their Open Font Licenses make the renderer independent of OS font installation.

The current name-based deterministic IDs are appropriate for new entries. Existing module entries require identity reconciliation before publication. Horde compilation fails explicitly pending canonical `hordeDamage` support. See the v1.4 contract and `INTEGRATION.md`.
