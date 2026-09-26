# Live validation in Foundry 14.368 / Daggerheart 2.10.5

Use a disposable copy of the upgraded world. Confirm `game.version` and `game.system.version`, the `cybermancer` asset root, and destination Actor folder IDs. Build the two regression packages with real production art, copy their packaged assets to the confirmed root, and import their JSON with the intended Cybermancy import path. Do not treat the sample art generated for local tests as production art.

After importing Cascade Burrowtail and Cascadia Mountain Valley, paste the following **read-only** script into the Foundry browser console. It checks document shape and asset responses; it does not create or modify Actors.

```js
const names = ["Cascade Burrowtail", "Cascadia Mountain Valley"];
const rows = await Promise.all(names.map(async name => {
  const matches = game.actors.filter(a => a.name === name);
  const a = matches[0];
  const sources = a ? [a.img, a.prototypeToken?.texture?.src].filter(Boolean) : [];
  const assets = await Promise.all(sources.map(async path => {
    try { const r = await fetch(path, {method: "HEAD"}); return {path, status: r.status}; }
    catch (e) { return {path, error: String(e)}; }
  }));
  return {
    name, matches: matches.length, type: a?.type,
    validationFailures: a?.validationFailures,
    tier: a?.system?.tier, difficulty: a?.system?.difficulty,
    fastPlay: Boolean(a?.getFlag("cybermancy", "fastPlay")),
    featureNames: a?.items.filter(i => i.type === "feature").map(i => i.name),
    featureForms: a?.items.filter(i => i.type === "feature").map(i => i.system.featureForm),
    mainAttackDamage: a?.type === "adversary" ? a.system.attack?.damage?.main?.value : undefined,
    potentialAdversaries: a?.type === "environment" ? a.system.potentialAdversaries : undefined,
    assets
  };
}));
console.log({foundry: game.version, daggerheart: game.system.version, rows});
```

Pass criteria: one Actor per name, matching types, no validation failures, complete feature lists, Fast Play present, successful image responses, and a Burrowtail main hit point damage field with custom formula `3`. Open the adversary sheet and use its attack and feature action; confirm the damage roll and chat output. Open the environment sheet and confirm every feature and GM note is visible. Export both Actors and compare their mechanical fields and feature text with the canonical specifications. If potential-adversary UUID mapping was supplied, confirm each link opens the intended Actor.

Run the combined adventure import macro twice and record imported/skipped/error counts. The second run should skip both existing Actors. If the macro includes legacy `_key`, `_stats`, fixed folder IDs, or asset-root assumptions, update its import adapter separately and repeat this test. Record exact installed patch versions, image root, folder IDs, any console errors, and the exported JSON before marking live validation PASS.
