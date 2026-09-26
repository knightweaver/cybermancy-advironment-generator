#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path


def load(p: Path): return json.loads(p.read_text(encoding='utf-8'))
def save(p: Path, d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(description='Migrate Cybermancy Entity Spec v1.0 to v1.1 using an already-authored Fast Play object.')
    ap.add_argument('--spec',required=True)
    ap.add_argument('--fast-play',required=True,help='JSON file containing {"prompts":[...],"goal":"..."}')
    ap.add_argument('--output',required=True)
    ap.add_argument('--custom-damage-formula')
    args=ap.parse_args()
    d=load(Path(args.spec)); fp=load(Path(args.fast_play))
    if d.get('specVersion')!='1.0': raise SystemExit('Input spec must be v1.0')
    if not isinstance(fp,dict) or 'prompts' not in fp or 'goal' not in fp: raise SystemExit('Fast Play JSON must contain prompts and goal')
    d['specVersion']='1.1'
    d['$schema']='schema/cybermancy-entity-spec-v1.1.schema.json'
    d['fastPlay']=fp
    if args.custom_damage_formula:
        if d.get('entityType')!='adversary': raise SystemExit('--custom-damage-formula applies only to adversaries')
        d['mechanics']['attack']['damage']['customFormula']=args.custom_damage_formula
    save(Path(args.output),d)

if __name__=='__main__': main()
