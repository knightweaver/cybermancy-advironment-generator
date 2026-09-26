#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'schema/cybermancy-entity-spec-v1.1.schema.json').read_text(encoding='utf-8'))
FIXTURES = ROOT / 'tests/fixtures'

spec = importlib.util.spec_from_file_location('cybermancy_package_builder', ROOT / 'src/package_builder.py')
pb = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(pb)


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def assert_min_pdf_font(pdf: Path, minimum: float = 9.95):
    doc = fitz.open(pdf)
    seen = []
    for page in doc:
        data = page.get_text('dict')
        for block in data.get('blocks', []):
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    text = span.get('text', '').strip()
                    if text:
                        seen.append((float(span.get('size', 0)), text))
    assert seen, f'No text spans found in {pdf}'
    small = [(size, text) for size, text in seen if size < minimum]
    assert not small, f'Text below {minimum} pt: {small[:8]}'


def run():
    fixtures = sorted(FIXTURES.glob('*.spec.json'))
    assert len(fixtures) >= 8, f'Expected eight locked Fast Play regression fixtures, got {len(fixtures)}'

    for path in fixtures:
        entity = load(path)
        schema_errors = pb.validate_schema(entity, SCHEMA)
        fp_errors, fp_warnings = pb.validate_fast_play(entity)
        path_errors = pb.validate_paths(entity)
        assert not schema_errors, (path.name, schema_errors)
        assert not fp_errors, (path.name, fp_errors)
        assert not fp_warnings, (path.name, fp_warnings)
        assert not path_errors, (path.name, path_errors)
        assert not pb.validate_target(entity), (path.name, pb.validate_target(entity))
        assert 2 <= len(entity['fastPlay']['prompts']) <= 5
        assert entity['fastPlay']['goal'].strip()
        assert 60 <= pb.fast_play_word_count(entity['fastPlay']) <= 110

        pm = pb.compile_print_model(entity)
        assert pm['fastPlay'] == entity['fastPlay']
        if entity['entityType'] == 'adversary':
            actor = pb.compile_adversary_foundry(entity, pb.DEFAULT_ADVERSARY_FOLDER)
            assert actor['flags']['cybermancy']['fastPlay'] == entity['fastPlay']
            assert 'FAST PLAY' in actor['system']['description']
            assert len(actor['_id']) == 16 and actor['_id'].isalnum()
            assert [x['name'] for x in actor['items']] == [x['name'] for x in entity['mechanics']['features']]
            assert isinstance(actor['system']['attack']['damage']['main'], dict)
            assert actor['system']['attack']['damage']['main']['applyTo'] == 'hitPoints'
            assert actor['system']['attack']['damage']['resources'] == {}
            assert 'parts' not in actor['system']['attack']['damage']
            assert 'bonuses' not in actor['system'] and 'rules' not in actor['system']
            assert 'hordeHp' not in actor['system']
            assert '_stats' not in actor
        else:
            actor = pb.compile_environment_foundry(entity, pb.DEFAULT_ENVIRONMENT_FOLDER)
            assert actor['flags']['cybermancy']['fastPlay'] == entity['fastPlay']
            assert 'FAST PLAY' in actor['system']['description']
            assert [x['name'] for x in actor['items']] == [x['name'] for x in entity['mechanics']['features']]
            assert all(x['type'] == 'feature' for x in actor['items'])
            assert isinstance(actor['system']['potentialAdversaries'], dict)
            assert actor['flags']['cybermancy']['potentialAdversaryNames'] == entity['mechanics']['potentialAdversaries']
            assert 'features' not in actor['system']
            assert isinstance(actor['system']['impulses'], str)
            assert actor['img'].startswith('modules/cybermancy/assets/')
            assert '_stats' not in actor

    burrow = load(FIXTURES / 'cascade-burrowtail.spec.json')
    burrow_actor = pb.compile_adversary_foundry(burrow, pb.DEFAULT_ADVERSARY_FOLDER)
    custom = burrow_actor['system']['attack']['damage']['main']['value']['custom']
    assert custom == {'enabled': True, 'formula': '3'}
    assert burrow_actor['img'] == 'modules/cybermancy/assets/images/adversaries/cascade-burrowtail.png'
    assert burrow_actor['prototypeToken']['texture']['src'] == 'modules/cybermancy/assets/tokens/adversaries/cascade-burrowtail-token.png'

    old_target = json.loads(json.dumps(burrow))
    old_target['foundry']['targetSystemVersion'] = '2.1.2'
    assert pb.validate_target(old_target), 'A mismatched Daggerheart source shape must fail.'
    horde = json.loads(json.dumps(burrow))
    horde['identity']['classification'] = 'horde'
    assert any('hordeDamage' in error for error in pb.validate_target(horde))

    valley = load(FIXTURES / 'cascadia-mountain-valley.spec.json')
    mapped_name = valley['mechanics']['potentialAdversaries'][0]
    mapped_uuid = 'Actor.1234567890abcdef'
    mapped = pb.compile_environment_foundry(valley, None, {mapped_name: mapped_uuid})
    group = next(iter(mapped['system']['potentialAdversaries'].values()))
    assert group['adversaries'] == [mapped_uuid]
    assert mapped_name not in mapped['system']['notes']
    assert 'Potential adversaries (unlinked)' in mapped['system']['notes']
    try:
        pb.compile_environment_foundry(valley, None, {mapped_name: 'Actor.nonexistent'})
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid UUID must fail')

    cougar = load(FIXTURES / 'altered-threshold-cougar.spec.json')
    pounce = next(f for f in cougar['mechanics']['features'] if f['name'] == 'Silent Threshold Pounce')['rules']
    assert 'become Vulnerable and Silenced until the end of their next action' in pounce

    # Renderer regression: render all eight locked entities, not merely the primary
    # adversary/environment examples. Every PDF must stay at >=10 pt, respect the
    # two-page contract, and place Fast Play before Features.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        portrait = td / 'portrait.png'
        env_art = td / 'environment.png'
        Image.new('RGB', (800, 1000), 'gray').save(portrait)
        Image.new('RGB', (900, 600), 'gray').save(env_art)
        opaque_token = td / 'opaque-token.png'
        Image.new('RGB', (512, 512), 'black').save(opaque_token)
        art_errors, _ = pb._validate_art([portrait, opaque_token], burrow)
        assert any('alpha channel' in error for error in art_errors)

        rendered = {}
        for fixture in fixtures:
            entity = load(fixture)
            out = td / f"{entity['identity']['slug']}.pdf"
            art = portrait if entity['entityType'] == 'adversary' else env_art
            meta = pb.render_pdf(entity, pb.compile_print_model(entity), art, out)
            assert not meta.get('layoutErrors'), (fixture.name, meta.get('layoutErrors'))
            doc = fitz.open(out)
            assert 1 <= len(doc) <= 2, f"{fixture.name}: unexpected page count {len(doc)}"
            assert_min_pdf_font(out)
            pdf_errors, _, _ = pb._validate_pdf(out)
            assert not pdf_errors, (fixture.name, pdf_errors)
            txt = ''.join(p.get_text() for p in doc)
            assert txt.index('FAST PLAY') < txt.index('FEATURES')
            rendered[entity['identity']['slug']] = out

        bp = rendered['cascade-burrowtail']
        assert len(fitz.open(bp)) == 1, 'Cascade Burrowtail reference should fit on one page.'

        # Visual-geometry regression for the two defects fixed in v1.2.1:
        # 1) MOTIVES & TACTICS must have visible separation from the description.
        # 2) EXPERIENCE label/value must share the first-line baseline.
        page = fitz.open(bp)[0]
        lines = []
        for block in page.get_text('dict').get('blocks', []):
            for line in block.get('lines', []):
                text = ''.join(span.get('text', '') for span in line.get('spans', [])).strip()
                if text:
                    lines.append((text, tuple(map(float, line['bbox']))))
        motives = next(b for t,b in lines if t == 'MOTIVES & TACTICS')
        prior = [b for t,b in lines if b[0] < 300 and b[3] <= motives[1] and t not in {'MOTIVES & TACTICS'}]
        previous_bottom = max(b[3] for b in prior)
        assert motives[1] - previous_bottom >= 6.0, f'Motives heading gap too small: {motives[1]-previous_bottom:.2f} pt'
        exp_label = next(b for t,b in lines if t == 'EXPERIENCE')
        exp_value = next(b for t,b in lines if t.startswith('Scurrying +2'))
        assert abs(exp_label[1] - exp_value[1]) <= 0.35, f'Experience baseline drift: {exp_label[1]} vs {exp_value[1]}'

    print(f'PASS: {len(fixtures)} Fast Play fixtures, Foundry compilation, schema validation, all-eight PDF renderer regressions, and v1.4.0 layout geometry checks.')


if __name__ == '__main__':
    run()
