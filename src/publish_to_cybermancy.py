#!/usr/bin/env python3
"""Stage approved, validated *new* packages into a Cybermancy source checkout."""

import argparse
import json
import re
import shutil
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def publish(packages, repo, write=False):
    repo = Path(repo).resolve()
    sources = repo / "src/packs/adventures"
    if not (repo / "module.json").is_file() or not all((sources / f).is_dir() for f in ("adversaries", "environments")):
        raise ValueError(f"Not a Cybermancy module checkout: {repo}")
    old_ids, old_names = set(), set()
    for family in ("adversaries", "environments"):
        for path in (sources / family).glob("*.json"):
            doc = read(path)
            if doc.get("type") in ("adversary", "environment"):
                old_ids.add(doc["_id"])
                old_names.add(doc["name"].casefold())
    planned, seen_ids, seen_names, seen_paths = [], set(), set(), set()
    for package in packages:
        root = Path(package).resolve()
        validation = read(root / "validation.json")
        if validation["status"] != "pass" or any(g["status"] != "pass" for g in validation["gates"]):
            raise ValueError(f"Package gates have not passed: {root}")
        slug = validation["slug"]
        spec_path, actor_path = root / "source" / f"{slug}.spec.json", root / "foundry" / f"{slug}.json"
        spec, actor = read(spec_path), read(actor_path)
        if spec.get("provenance", {}).get("status") != "approved" or slug != spec["identity"]["slug"] or actor["name"] != spec["identity"]["name"]:
            raise ValueError(f"Unapproved or mismatched identity: {slug}")
        family = {"adversary": "adversaries", "environment": "environments"}.get(actor["type"])
        if family is None or spec["entityType"] != actor["type"]:
            raise ValueError(f"Package type mismatch: {slug}")
        if actor["_id"] in old_ids | seen_ids or actor["name"].casefold() in old_names | seen_names:
            raise ValueError(f"Actor ID/name already exists; reconcile published identities: {actor['name']}")
        seen_ids.add(actor["_id"])
        seen_names.add(actor["name"].casefold())
        folder = actor.get("folder")
        folder_file = next((p for p in (sources / family).glob("*.json") if p.stem.endswith("_" + str(folder))), None)
        if not folder or not folder_file or read(folder_file).get("name") != f"Tier {spec['identity']['tier']}":
            raise ValueError(f"Unverified Tier folder for {actor['name']}: {folder}")
        items = actor["items"]
        item_ids = [item["_id"] for item in items]
        action_ids = [aid for item in items for aid in item["system"]["actions"]]
        if len(item_ids) != len(set(item_ids)) or len(action_ids) != len(set(action_ids)):
            raise ValueError(f"Embedded ID collision: {slug}")
        if actor.get("_key") != f"!actors!{actor['_id']}" or any(i.get("_key") != f"!actors.items!{actor['_id']}.{i['_id']}" for i in items):
            raise ValueError(f"Incorrect Actor/Item key: {slug}")
        name = re.sub(r"[^A-Za-z0-9]+", "_", actor["name"]).strip("_")
        files = [(actor_path, sources / family / f"{name}_{actor['_id']}.json")]
        for art in spec["art"].values():
            path = art["path"]
            if not path.startswith("modules/cybermancy/assets/"):
                raise ValueError(f"Non-module art path: {path}")
            rel = path.removeprefix("modules/cybermancy/")
            files.append((root / rel, repo / rel))
        authoring = repo / "authoring/advironments"
        files += [(spec_path, authoring / f"{slug}.spec.json"),
                  (root / "validation.json", authoring / f"{slug}.validation.json")]
        for source, dest in files:
            if not source.is_file() or dest.is_file() or dest in seen_paths:
                raise ValueError(f"Source missing or destination occupied: {source} -> {dest}")
            seen_paths.add(dest)
        planned.extend(files)
    if write:
        for source, dest in planned:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.name.endswith(".spec.json"):
                spec = read(source)
                spec["$schema"] = "https://raw.githubusercontent.com/knightweaver/cybermancy-advironment-generator/main/schema/cybermancy-entity-spec-v1.1.schema.json"
                dest.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            else:
                shutil.copy2(source, dest)
    return [str(dest.relative_to(repo)) for _, dest in planned]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cybermancy-repo", required=True)
    parser.add_argument("--package", required=True, action="append")
    parser.add_argument("--write", action="store_true", help="Stage after preflight; default dry-run")
    args = parser.parse_args()
    for path in publish(args.package, args.cybermancy_repo, args.write):
        print(("STAGED " if args.write else "WOULD STAGE ") + path)


if __name__ == "__main__":
    main()
