#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import os
import re
import shutil
import string
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from jsonschema import Draft202012Validator
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from pypdf import PdfReader
import fitz

BUILDER_VERSION = "1.4.0"
PACKAGE_FORMAT = "cybermancy-entity-package-v1"
DEFAULT_CORE = "14.368"
DEFAULT_SYSTEM = "2.10.5"
DEFAULT_ADVERSARY_FOLDER = None
DEFAULT_ENVIRONMENT_FOLDER = None
PDF_STYLE = "cybermancy-daggerheart-reference"
MIN_BODY_PT = 10.0

# Print palette
PAPER = colors.HexColor("#F8F4E8")
CARD = colors.HexColor("#FBF8F0")
WHITE = colors.white
GOLD = colors.HexColor("#C7A75C")
PURPLE = colors.HexColor("#5A337B")
GREEN = colors.HexColor("#4B7256")
TEXT = colors.HexColor("#242424")
MUTED = colors.HexColor("#56504A")

FONT_DIR = Path(__file__).resolve().parents[1] / "fonts"
FONT_FILES = {
    "PTSans": FONT_DIR / "PT_Sans-Web-Regular.ttf",
    "PTSans-Italic": FONT_DIR / "PT_Sans-Web-Italic.ttf",
    "PTSans-Bold": FONT_DIR / "PT_Sans-Web-Bold.ttf",
    "PTSans-BoldItalic": FONT_DIR / "PT_Sans-Web-BoldItalic.ttf",
    "PTSansNarrow": FONT_DIR / "PT_Sans-Narrow-Web-Regular.ttf",
    "PTSansNarrow-Bold": FONT_DIR / "PT_Sans-Narrow-Web-Bold.ttf",
}


def register_fonts() -> None:
    for name, path in FONT_FILES.items():
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(path)))


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def stable_id(*parts: str) -> str:
    alphabet = string.ascii_letters + string.digits
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).digest()
    value = int.from_bytes(digest[:16], "big")
    chars = []
    for _ in range(16):
        value, rem = divmod(value, len(alphabet))
        chars.append(alphabet[rem])
    return "".join(chars)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def words(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", text))


def fast_play_word_count(fp: Dict[str, Any]) -> int:
    return sum(words(p["text"]) for p in fp["prompts"]) + words(fp["goal"])


def validate_schema(spec: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    errors = []
    for err in sorted(Draft202012Validator(schema).iter_errors(spec), key=lambda e: list(e.path)):
        loc = ".".join(str(x) for x in err.path) or "$"
        errors.append(f"{loc}: {err.message}")
    return errors


def validate_fast_play(spec: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    fp = spec.get("fastPlay") or {}
    prompts = fp.get("prompts", [])
    features = {f["name"] for f in spec.get("mechanics", {}).get("features", [])}
    for i, p in enumerate(prompts):
        for ref in p.get("featureRefs", []):
            if ref not in features:
                errors.append(f"Fast Play prompt {i+1} references missing feature: {ref}")
    wc = fast_play_word_count(fp) if fp else 0
    if fp and not (60 <= wc <= 110):
        warnings.append(f"Fast Play is {wc} words; target is approximately 60-110 words.")
    labels = [p.get("label", "").strip().casefold() for p in prompts]
    if len(labels) != len(set(labels)):
        warnings.append("Fast Play contains duplicate prompt labels; confirm this is deliberate.")
    if fp and not fp.get("goal", "").strip():
        errors.append("Fast Play goal is required.")
    return errors, warnings


def validate_paths(spec: Dict[str, Any]) -> List[str]:
    slug = spec["identity"]["slug"]
    errors = []
    if spec["entityType"] == "adversary":
        expected = {
            "portrait": f"modules/cybermancy/assets/images/adversaries/{slug}.png",
            "token": f"modules/cybermancy/assets/tokens/adversaries/{slug}-token.png",
        }
    else:
        expected = {"environment": f"modules/cybermancy/assets/images/environments/{slug}.png"}
    for key, value in expected.items():
        got = spec.get("art", {}).get(key, {}).get("path")
        if got != value:
            errors.append(f"art.{key}.path must be {value!r}, got {got!r}")
    return errors


def validate_target(spec: Dict[str, Any]) -> List[str]:
    target = spec.get("foundry", {})
    core = target.get("targetCoreVersion", "")
    system = target.get("targetSystemVersion", "")
    errors = []
    if core != DEFAULT_CORE or system != DEFAULT_SYSTEM:
        errors.append(f"Package Builder v1.4.0 has source-shape qualification for Foundry {DEFAULT_CORE} / Daggerheart {DEFAULT_SYSTEM}; update the compiler and tests before changing this target.")
    if spec.get("entityType") == "adversary" and spec.get("identity", {}).get("classification") == "horde":
        errors.append("Horde needs explicit Daggerheart 2 typeData.hordeDamage; Entity Spec v1.1 has no canonical field for it. Do not silently use the system default.")
    return errors


def feature_type_to_action_type(feature_type: str) -> str:
    if feature_type == "passive":
        return "passive"
    if feature_type in ("reaction", "triggered"):
        return "reaction"
    return "action"


def rules_html(text: str) -> str:
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return "".join(f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in parts)


def fast_play_html(spec: Dict[str, Any]) -> str:
    fp = spec["fastPlay"]
    rows = []
    for p in fp["prompts"]:
        rows.append(
            f"<p><strong><em>{html.escape(p['label'])}:</em></strong> {html.escape(p['text'])}</p>"
        )
    rows.append(f"<p><strong><em>Goal:</em></strong> {html.escape(fp['goal'])}</p>")
    return '<section class="cybermancy-fast-play"><h3>FAST PLAY</h3>' + "".join(rows) + "</section>"


def compile_attack(spec: Dict[str, Any], actor_id: str) -> Dict[str, Any]:
    attack = spec["mechanics"]["attack"]
    dmg = attack["damage"]
    custom_formula = dmg.get("customFormula")
    return {
        "name": attack["name"],
        "roll": {
            "bonus": attack["bonus"], "type": "attack", "trait": None, "difficulty": None,
            "advState": "neutral",
            "diceRolling": {"multiplier": "prof", "flatMultiplier": 1, "dice": "d6", "compare": None, "treshold": None},
            "useDefault": False,
        },
        "range": attack["range"],
        "damage": {
            "main": {
                "value": {
                    "custom": {"enabled": bool(custom_formula), "formula": custom_formula or ""},
                    "dice": dmg["die"], "bonus": dmg["bonus"], "multiplier": "flat", "flatMultiplier": dmg["count"],
                },
                "applyTo": "hitPoints", "type": dmg["types"], "resultBased": False,
                "valueAlt": {"multiplier": "prof", "flatMultiplier": 1, "dice": "d6", "bonus": None, "custom": {"enabled": False, "formula": ""}},
                "base": False, "includeBase": False, "direct": False,
                "fullRestore": False, "itemId": None,
            },
            "resources": {},
        },
        "img": "icons/creatures/abilities/mouth-teeth-human.webp",
        "type": "attack", "chatDisplay": False,
        "_id": stable_id(spec["identity"]["slug"], "standard-attack"),
        "systemPath": "actions", "baseAction": False, "description": "",
        "originItem": {"type": "itemCollection"}, "actionType": "action", "cost": [],
        "triggers": [], "areas": [],
        "uses": {"value": None, "max": None, "recovery": None, "consumeOnSuccess": False},
        "target": {"type": "any", "amount": None}, "effects": [],
        "save": {"trait": None, "difficulty": None, "damageMod": "none"},
    }


def compile_feature_item(spec: Dict[str, Any], actor_id: str, feature: Dict[str, Any], index: int) -> Dict[str, Any]:
    slug = spec["identity"]["slug"]
    item_id = stable_id(slug, "feature", feature["name"])
    action_id = stable_id(slug, "feature-action", feature["name"])
    desc = rules_html(feature["rules"])
    action_type = feature_type_to_action_type(feature["featureType"])
    return {
        "name": feature["name"], "type": "feature", "_id": item_id, "img": "icons/svg/aura.svg",
        "system": {
            "description": desc, "resource": None,
            "actions": {
                action_id: {
                    "type": "effect", "_id": action_id, "systemPath": "actions", "description": desc,
                    "chatDisplay": True, "actionType": action_type, "cost": [],
                    "uses": {"value": None, "max": "", "recovery": None, "consumeOnSuccess": False},
                    "effects": [], "target": {"type": "any", "amount": None}, "name": feature["name"],
                    "img": "icons/svg/aura.svg", "range": "", "baseAction": False,
                    "originItem": {"type": "itemCollection"}, "triggers": [], "areas": [],
                }
            },
            "featureForm": action_type, "attribution": {}, "gmNotes": "",
            "granter": None, "actorResources": [],
        },
        "effects": [], "folder": None, "sort": index * 100000, "flags": {},
        "ownership": {"default": 0},
        "_key": f"!actors.items!{actor_id}.{item_id}",
    }


def prototype_token(spec: Dict[str, Any]) -> Dict[str, Any]:
    slug = spec["identity"]["slug"]
    token_path = spec["art"]["token"]["path"]
    return {
        "name": spec["identity"]["name"], "displayName": 0, "actorLink": False, "width": 1, "height": 1,
        "texture": {"src": token_path, "anchorX": 0.5, "anchorY": 0.5, "offsetX": 0, "offsetY": 0, "fit": "contain", "scaleX": 1, "scaleY": 1, "rotation": 0, "tint": "#ffffff", "alphaThreshold": 0.75},
        "lockRotation": False, "rotation": 0, "alpha": 1, "disposition": -1, "displayBars": 0,
        "bar1": {"attribute": "resources.hitPoints"}, "bar2": {"attribute": "resources.stress"},
        "light": {"negative": False, "priority": 0, "alpha": 0.5, "angle": 360, "bright": 0, "color": None, "coloration": 1, "dim": 0, "attenuation": 0.5, "luminosity": 0.5, "saturation": 0, "contrast": 0, "shadows": 0, "animation": {"type": None, "speed": 5, "intensity": 5, "reverse": False}, "darkness": {"min": 0, "max": 1}},
        "sight": {"enabled": False, "range": 0, "angle": 360, "visionMode": "basic", "color": None, "attenuation": 0.1, "brightness": 0, "saturation": 0, "contrast": 0},
        "detectionModes": [], "occludable": {"radius": 0},
        "ring": {"enabled": bool(spec["foundry"].get("tokenRing", True)), "colors": {"ring": "#4d4033", "background": None}, "effects": 1, "subject": {"scale": 0.8, "texture": None}},
        "turnMarker": {"mode": 1, "animation": None, "src": None, "disposition": False},
        "movementAction": None, "flags": {}, "randomImg": False, "appendNumber": False, "prependAdjective": False,
    }


def compile_adversary_foundry(spec: Dict[str, Any], folder_id: Optional[str]) -> Dict[str, Any]:
    identity, design, mech = spec["identity"], spec["design"], spec["mechanics"]
    actor_id = stable_id(identity["slug"], "actor")
    experiences = {}
    for e in mech.get("experiences", []):
        experiences[stable_id(identity["slug"], "experience", e["name"])] = {"name": e["name"], "value": e["value"], "description": ""}
    description = f"<p>{html.escape(identity['description'])}</p>" + fast_play_html(spec)
    items = [compile_feature_item(spec, actor_id, f, i) for i, f in enumerate(mech["features"])]
    actor = {
        "name": identity["name"], "img": spec["art"]["portrait"]["path"], "type": "adversary", "folder": folder_id,
        "system": {
            "difficulty": mech["difficulty"], "damageThresholds": mech["damageThresholds"],
            "resources": {
                "hitPoints": {"value": 0, "max": mech["hitPoints"], "isReversed": True},
                "stress": {"value": 0, "max": mech["stress"], "isReversed": True},
            },
            "motivesAndTactics": ", ".join(design.get("motivesAndTactics", [])),
            "resistance": {
                "physical": {"resistance": bool(mech.get("physicalResistance", False)), "immunity": False, "reduction": 0},
                "magical": {"resistance": bool(mech.get("magicalResistance", False)), "immunity": False, "reduction": 0},
            },
            "type": identity["classification"], "notes": "",
            "experiences": experiences,
            "tier": identity["tier"], "description": description,
            "attack": compile_attack(spec, actor_id),
            "attribution": {"source": spec["foundry"]["attributionSource"], "page": None, "artist": ""},
            "criticalThreshold": 20,
        },
        "flags": {"cybermancy": {"fastPlay": copy.deepcopy(spec["fastPlay"]), "specVersion": spec["specVersion"], "packageBuilderVersion": BUILDER_VERSION}},
        "prototypeToken": prototype_token(spec), "items": items, "effects": [], "ownership": {"default": 0},
        "_id": actor_id, "sort": 0, "_key": f"!actors!{actor_id}",
    }
    return actor


def compile_environment_foundry(spec: Dict[str, Any], folder_id: Optional[str], adversary_uuids: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    identity, design, mech = spec["identity"], spec["design"], spec["mechanics"]
    actor_id = stable_id(identity["slug"], "actor")
    features = [compile_feature_item(spec, actor_id, f, i) for i, f in enumerate(mech["features"])]
    adversary_uuids = adversary_uuids or {}
    names = mech["potentialAdversaries"]
    unknown_names = set(adversary_uuids) - set(names)
    if unknown_names:
        raise ValueError(f"UUID map contains names absent from this environment: {sorted(unknown_names)}")
    resolved = [adversary_uuids[name] for name in names if name in adversary_uuids]
    unresolved = [name for name in names if name not in adversary_uuids]
    for uuid in resolved:
        if not re.fullmatch(r"(?:Actor\.[A-Za-z0-9]{16}|Compendium\.[^.]+\.[^.]+\.Actor\.[A-Za-z0-9]{16})", uuid):
            raise ValueError(f"Invalid potential-adversary Actor UUID: {uuid!r}")
    potential = {}
    if resolved:
        group_id = stable_id(identity["slug"], "potential-adversaries")
        potential[group_id] = {"label": "Potential Adversaries", "adversaries": resolved}
    description = f"<p>{html.escape(identity['description'])}</p>" + fast_play_html(spec)
    notes = f"<p>{html.escape(design['encounterPurpose'])}</p>"
    if unresolved:
        notes += "<p><strong>Potential adversaries (unlinked):</strong> " + html.escape(", ".join(unresolved)) + "</p>"
    return {
        "name": identity["name"], "type": "environment", "img": spec["art"]["environment"]["path"], "folder": folder_id,
        "system": {
            "description": description,
            "tier": identity["tier"], "type": identity["classification"], "difficulty": mech["difficulty"],
            "notes": notes, "impulses": ", ".join(mech["impulses"]), "potentialAdversaries": potential,
            "attribution": {"source": spec["foundry"]["attributionSource"], "page": None, "artist": ""},
        },
        "items": features, "effects": [], "ownership": {"default": 0},
        "flags": {"cybermancy": {"targetCoreVersion": spec["foundry"]["targetCoreVersion"], "targetSystemVersion": spec["foundry"]["targetSystemVersion"], "potentialAdversaryNames": names, "tags": design.get("tags", []), "fastPlay": copy.deepcopy(spec["fastPlay"]), "specVersion": spec["specVersion"], "packageBuilderVersion": BUILDER_VERSION}},
        "_id": actor_id, "sort": 0, "_key": f"!actors!{actor_id}",
    }


def compile_print_model(spec: Dict[str, Any]) -> Dict[str, Any]:
    ident, mech = spec["identity"], spec["mechanics"]
    base = {
        "entity": ident["name"], "slug": ident["slug"], "pageTarget": spec["print"]["pageTarget"],
        "style": spec["print"]["style"], "includeArt": spec["print"]["includeArt"],
        "title": ident["name"], "subtitle": f"Tier {ident['tier']} {ident['classification'].title()}",
        "description": ident["description"], "difficulty": mech["difficulty"], "fastPlay": copy.deepcopy(spec["fastPlay"]),
        "features": [{"name": f["name"], "featureType": f["featureType"], "rules": f["rules"]} for f in mech["features"]],
    }
    if spec["entityType"] == "adversary":
        dmg = mech["attack"]["damage"]
        formula = dmg.get("customFormula") or f"{'' if dmg['count']==1 else dmg['count']}{dmg['die']}{'+'+str(dmg['bonus']) if dmg['bonus']>0 else str(dmg['bonus']) if dmg['bonus']<0 else ''}"
        base.update({
            "motivesAndTactics": spec["design"].get("motivesAndTactics", []), "damageThresholds": mech["damageThresholds"],
            "hitPoints": mech["hitPoints"], "stress": mech["stress"],
            "attack": {"name": mech["attack"]["name"], "bonus": mech["attack"]["bonus"], "range": mech["attack"]["range"], "damage": f"{formula} {'/'.join(dmg['types'])}"},
            "experiences": mech.get("experiences", []),
        })
    else:
        base.update({"impulses": mech["impulses"], "potentialAdversaries": mech["potentialAdversaries"]})
    return base


def _style(name: str, font: str, size: float, leading: Optional[float] = None, color=TEXT, space_after=0):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=leading or size*1.16, textColor=color, spaceAfter=space_after)


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def _draw_para(c: canvas.Canvas, text: str, style: ParagraphStyle, x: float, y_top: float, w: float) -> float:
    p = _p(text, style)
    _, h = p.wrap(w, 1000)
    p.drawOn(c, x, y_top-h)
    return h


def _draw_card(c: canvas.Canvas, x: float, y_bottom: float, w: float, h: float, radius: float=7, fill=CARD) -> None:
    c.setFillColor(fill); c.setStrokeColor(GOLD); c.setLineWidth(0.8)
    c.roundRect(x, y_bottom, w, h, radius, fill=1, stroke=1)


def _para_height(text: str, style: ParagraphStyle, width: float) -> float:
    p = _p(text, style)
    _, h = p.wrap(width, 1000)
    return h


def _draw_label_value_row(
    c: canvas.Canvas,
    x: float,
    y_top: float,
    width: float,
    label: str,
    value_html: str,
    value_style: ParagraphStyle,
    *,
    label_width: float = 82,
    gap: float = 8,
    label_font: str = 'PTSans-Bold',
    label_size: float = 10,
    label_color=PURPLE,
) -> float:
    """Measured label/value row with a shared first-line baseline.

    The label is right aligned into a fixed column; the wrapped value begins at a
    stable left edge. This avoids the hard-coded baseline drift that previously
    affected EXPERIENCE rows.
    """
    value_x = x + label_width + gap
    value_w = width - label_width - gap
    p = _p(value_html, value_style)
    _, h = p.wrap(value_w, 1000)
    c.setFillColor(label_color)
    c.setFont(label_font, label_size)
    # Match the first line baseline used by a 10 pt Paragraph with ~11.4 leading.
    c.drawRightString(x + label_width, y_top - 10.0, label)
    p.drawOn(c, value_x, y_top - h)
    return max(h, value_style.leading)


def _draw_attack_row(
    c: canvas.Canvas,
    x: float,
    y_top: float,
    width: float,
    attack: Dict[str, Any],
    styles: Dict[str, ParagraphStyle],
) -> float:
    """Collision-safe attack summary at the 10 pt minimum.

    Prefer one line. If the name and range/damage would collide, the range/damage
    moves to a second indented line instead of shrinking text below 10 pt.
    """
    label = f"ATK +{attack['bonus']}"
    name = str(attack['name']).upper()
    range_text = str(attack['range']).replace('veryClose','Very Close').replace('veryFar','Very Far').title()
    right_text = f"{range_text}   {attack['damage']}"
    label_w = max(58.0, pdfmetrics.stringWidth(label, 'PTSans-Bold', 10) + 4)
    gap = 8.0
    right_w = pdfmetrics.stringWidth(right_text, 'PTSans', 10)
    name_x = x + label_w + gap
    one_line_name_w = width - label_w - gap - right_w - 10
    name_w = pdfmetrics.stringWidth(name, 'PTSans-Bold', 10)

    c.setFillColor(PURPLE)
    c.setFont('PTSans-Bold', 10)
    c.drawString(x, y_top - 9.0, label)
    c.setFillColor(TEXT)
    c.setFont('PTSans-Bold', 10)

    if one_line_name_w >= 70 and name_w <= one_line_name_w:
        c.drawString(name_x, y_top - 9.0, name)
        c.setFont('PTSans', 10)
        c.drawRightString(x + width, y_top - 9.0, right_text)
        return 12.0

    # Two-line fallback: preserve font size and give the attack name the full
    # remaining first-row width. Wrap only when genuinely necessary.
    name_para = _p(html.escape(name), _style('attackname','PTSans-Bold',10,11.4))
    _, name_h = name_para.wrap(width - label_w - gap, 1000)
    name_para.drawOn(c, name_x, y_top - name_h)
    second_y = y_top - max(12.0, name_h) - 1.0
    c.setFont('PTSans', 10)
    c.drawRightString(x + width, second_y - 9.0, right_text)
    return max(12.0, name_h) + 12.0


def _measure_environment_summary(mech: Dict[str, Any], styles: Dict[str, ParagraphStyle], left_w: float) -> float:
    impulses = mech.get('impulses', [])[:5]
    impulse_h = 0.0
    for imp in impulses:
        impulse_h += _para_height('• ' + html.escape(imp), styles['body'], left_w - 32) + 1
    # Top difficulty row + impulses heading + measured impulse text + padding.
    return max(96.0, 62.0 + impulse_h + 12.0)


def _measure_potential_adversaries(text: str, styles: Dict[str, ParagraphStyle], width: float) -> float:
    body_h = _para_height(html.escape(text), styles['body'], width - 20)
    return 12.0 + 12.0 + 5.0 + body_h + 10.0


def _image_fit(path: Path, box_w: float, box_h: float) -> Tuple[float, float]:
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(box_w/iw, box_h/ih)
    return iw*scale, ih*scale


def _feature_flow_height(features: List[Dict[str, Any]], width: float, styles: Dict[str, ParagraphStyle]) -> float:
    total = 0.0
    for f in features:
        head = f"<b>{html.escape(f['name'].upper())}</b> &nbsp; <font name='PTSans-BoldItalic'>{html.escape(f['featureType'].title())}</font>"
        p1=_p(head, styles['feature_head']); _,h1=p1.wrap(width,1000)
        p2=_p(html.escape(f['rules']).replace('\n\n','<br/>').replace('\n',' '), styles['body']); _,h2=p2.wrap(width,1000)
        total += h1+h2+5
    return total


def render_pdf(spec: Dict[str, Any], print_model: Dict[str, Any], art_path: Path, out_pdf: Path) -> Dict[str, Any]:
    register_fonts()
    W,H = letter
    c = canvas.Canvas(str(out_pdf), pagesize=letter)
    c.setTitle(f"{spec['identity']['name']} - Cybermancy GM Reference")
    c.setAuthor("Cybermancy")
    styles = {
        'body': _style('body','PTSans',10,11.4),
        'body_italic': _style('bodyitalic','PTSans-Italic',10,11.6),
        'small_bold': _style('smallbold','PTSans-Bold',10,11.4,PURPLE),
        'fp': _style('fp','PTSans',10,11.5),
        'feature_head': _style('featurehead','PTSans-Bold',10,11.4,PURPLE),
    }
    margin=42; gap=14; col=(W-2*margin-gap)/2
    usable_top=H-42
    safe_content_bottom=48
    card_content_bottom=70
    layout_errors: List[str] = []
    layout_warnings: List[str] = []
    layout_metrics: Dict[str, Any] = {}

    def base_page():
        c.setFillColor(PAPER); c.rect(0,0,W,H,fill=1,stroke=0)
        c.setStrokeColor(GOLD); c.setLineWidth(0.8); c.line(margin,30,W-margin,30)
        c.setFillColor(MUTED); c.setFont('PTSans',10)
        c.drawString(margin,16,'CYBERMANCY // GM REFERENCE')
        c.drawRightString(W-margin,16,'DAGGERHEART-COMPATIBLE HOMEBREW')

    def draw_fast_play(x: float, top: float, width: float) -> float:
        fp=spec['fastPlay']
        rows=[]
        for pr in fp['prompts']:
            rows.append(f"<font name='PTSans-BoldItalic'>{html.escape(pr['label'])}:</font> {html.escape(pr['text'])}")
        rows.append(f"<font name='PTSans-BoldItalic'>Goal:</font> {html.escape(fp['goal'])}")
        heights=[]
        for row in rows:
            p=_p(row,styles['fp']); _,h=p.wrap(width-16,1000); heights.append(h)
        total=25+sum(heights)+2*(len(rows)-1)+12
        _draw_card(c,x,top-total,width,total,fill=colors.HexColor('#F3EEDC'))
        c.setFillColor(PURPLE); c.setFont('PTSansNarrow-Bold',11.5); c.drawString(x+8,top-18,'FAST PLAY')
        y=top-28
        for row,h in zip(rows,heights):
            p=_p(row,styles['fp']); p.wrapOn(c,width-16,1000); p.drawOn(c,x+8,y-h); y-=h+2
        return total

    def draw_feature_block(x: float, y_top: float, width: float, feature: Dict[str, Any], *, environment: bool=False) -> float:
        if environment:
            head=f"<b>{html.escape(feature['name'])}</b> - <font name='PTSans-BoldItalic'>{html.escape(feature['featureType'].title())}</font>"
        else:
            head=f"<b>{html.escape(feature['name'].upper())}</b> &nbsp; <font name='PTSans-BoldItalic'>{html.escape(feature['featureType'].title())}</font>"
        p1=_p(head,styles['feature_head']); _,h1=p1.wrap(width,1000)
        body=html.escape(feature['rules']).replace('\n\n','<br/>').replace('\n',' ')
        p2=_p(body,styles['body']); _,h2=p2.wrap(width,1000)
        p1.drawOn(c,x,y_top-h1)
        p2.drawOn(c,x,y_top-h1-h2)
        return h1+h2+5

    base_page()
    ident=spec['identity']; mech=spec['mechanics']
    if spec['entityType']=='adversary':
        left_x=margin; right_x=margin+col+gap; top=usable_top
        _draw_card(c,left_x,58,col,top-58)
        x=left_x+14; w=col-28; y=top-18
        c.setFillColor(PURPLE)
        title=ident['name'].upper()
        size=22.0
        while pdfmetrics.stringWidth(title,'PTSansNarrow-Bold',size)>w and size>17:
            size-=0.5
        c.setFont('PTSansNarrow-Bold',size); c.drawString(x,y,title); y-=28
        c.setFillColor(TEXT); c.setFont('PTSans-Italic',11); c.drawString(x,y,f"Tier {ident['tier']} {ident['classification'].title()}"); y-=20

        # Description -> section heading spacing is deliberately measured. The old
        # renderer used a 7 pt hand-tuned gap that crowded MOTIVES & TACTICS.
        h=_draw_para(c,html.escape(ident['description']),styles['body_italic'],x,y,w)
        y-=h
        motives_gap=18.0
        y-=motives_gap
        c.setFillColor(PURPLE); c.setFont('PTSans-Bold',10.5); c.drawString(x,y,'MOTIVES & TACTICS')
        y-=15
        h=_draw_para(c,html.escape(', '.join(spec['design'].get('motivesAndTactics',[]))),styles['body'],x,y,w)
        y-=h+12
        layout_metrics['motivesGapAfterDescriptionPt']=motives_gap

        box_h=54; _draw_card(c,x,y-box_h,w,box_h,5,WHITE)
        thr=mech['damageThresholds']
        thr_text=(f"{thr.get('major')} / {thr.get('severe')}" if thr.get('major') is not None and thr.get('severe') is not None else '- / -')
        labels=['DIFFICULTY','THRESHOLDS','HP','STRESS']; vals=[str(mech['difficulty']),thr_text,str(mech['hitPoints']),str(mech['stress'])]
        for i,(lab,val) in enumerate(zip(labels,vals)):
            cx=x+(i+0.5)*w/4
            c.setFillColor(MUTED); c.setFont('PTSansNarrow-Bold',10); c.drawCentredString(cx,y-16,lab)
            c.setFillColor(TEXT); c.setFont('PTSans-Bold',13.5); c.drawCentredString(cx,y-39,val)
        y-=box_h+12

        atk=print_model['attack']
        attack_h=_draw_attack_row(c,x,y,w,atk,styles)
        y-=attack_h+10

        if mech.get('experiences'):
            exp=', '.join(f"{e['name']} +{e['value']}" for e in mech['experiences'])
            exp_h=_draw_label_value_row(c,x,y,w,'EXPERIENCE',html.escape(exp),styles['body'])
            layout_metrics['experienceRowHeightPt']=exp_h
            y-=exp_h+12

        fp_top=y
        fp_h=draw_fast_play(x,fp_top,w)
        fp_bottom=fp_top-fp_h
        y=fp_bottom-8
        layout_metrics['leftContentBottomPt']=fp_bottom
        layout_metrics['leftSafeBottomPt']=card_content_bottom
        if fp_bottom < card_content_bottom:
            layout_errors.append(
                f"Adversary left-column content reaches {fp_bottom:.1f} pt; safe card content bottom is {card_content_bottom:.1f} pt. Shorten text or permit a layout revision."
            )

        c.setFillColor(PURPLE); c.setFont('PTSansNarrow-Bold',14); c.drawString(right_x,top-4,'FEATURES')
        fy=top-23; fw=col
        features=print_model['features']
        right_bottom=58
        feature_total=_feature_flow_height(features,fw,styles)
        right_available=fy-right_bottom
        art_on_right=False
        art_on_left=False
        right_art_h=0.0
        if art_path.exists():
            desired_h=min(200.0,max(135.0,right_available-feature_total-12.0))
            if feature_total+12.0+desired_h <= right_available:
                art_on_right=True; right_art_h=desired_h
            else:
                left_art_available=max(0.0,y-70.0)
                if left_art_available >= 125.0:
                    art_on_left=True
                else:
                    art_on_right=True; right_art_h=125.0
        feature_limit=right_bottom+(right_art_h+12 if art_on_right else 0)
        remaining=[]
        for idx,f in enumerate(features):
            head=f"<b>{html.escape(f['name'].upper())}</b> &nbsp; <font name='PTSans-BoldItalic'>{html.escape(f['featureType'].title())}</font>"
            p1=_p(head,styles['feature_head']); _,h1=p1.wrap(fw,1000)
            body=html.escape(f['rules']).replace('\n\n','<br/>').replace('\n',' ')
            p2=_p(body,styles['body']); _,h2=p2.wrap(fw,1000)
            need=h1+h2+5
            if fy-need < feature_limit:
                remaining=features[idx:]
                break
            p1.drawOn(c,right_x,fy-h1); fy-=h1
            p2.drawOn(c,right_x,fy-h2); fy-=h2+5
        if art_path.exists() and art_on_right:
            iw,ih=_image_fit(art_path,fw,right_art_h)
            ix=right_x+(fw-iw)/2; iy=58+(right_art_h-ih)/2
            c.drawImage(ImageReader(str(art_path)),ix,iy,width=iw,height=ih,preserveAspectRatio=True,mask='auto')
        elif art_path.exists() and art_on_left:
            art_box_top=y-2
            art_box_bottom=68
            art_box_h=max(0.0,art_box_top-art_box_bottom)
            if art_box_h >= 125:
                iw,ih=_image_fit(art_path,w,art_box_h)
                ix=x+(w-iw)/2; iy=art_box_bottom+(art_box_h-ih)/2
                c.drawImage(ImageReader(str(art_path)),ix,iy,width=iw,height=ih,preserveAspectRatio=True,mask='auto')
        if remaining:
            c.showPage(); base_page()
            c.setFillColor(PURPLE); c.setFont('PTSansNarrow-Bold',18); c.drawString(margin,usable_top-4,f"{ident['name'].upper()} - FEATURES")
            y2=usable_top-28
            fullw=W-2*margin
            for f in remaining:
                need=_feature_flow_height([f],fullw,styles)
                if y2-need < safe_content_bottom:
                    layout_errors.append('Adversary feature continuation exceeds the supported two-page printable area.')
                    break
                used=draw_feature_block(margin,y2,fullw,f,environment=False)
                y2-=used+2
    else:
        # Environment: title/description -> content-aware summary/art -> Fast Play -> Features.
        top=usable_top
        c.setFillColor(TEXT)
        title=ident['name'].upper(); size=24.0
        while pdfmetrics.stringWidth(title,'PTSansNarrow-Bold',size)>W-2*margin and size>17:
            size-=0.5
        c.setFont('PTSansNarrow-Bold',size); c.drawString(margin,top,title); top-=23
        c.setFont('PTSans',11); c.drawString(margin,top,f"Tier {ident['tier']} {ident['classification'].title()}"); top-=18
        h=_draw_para(c,html.escape(ident['description']),styles['body'],margin,top,W-2*margin); top-=h+12

        left_w=250; art_x=margin+left_w+14; art_w=W-margin-art_x
        box_h=_measure_environment_summary(mech,styles,left_w)
        layout_metrics['environmentSummaryHeightPt']=box_h
        _draw_card(c,margin,top-box_h,left_w,box_h,7,WHITE)
        c.setFillColor(TEXT); c.setFont('PTSans-Bold',11); c.drawString(margin+14,top-20,'DIFFICULTY')
        c.setFont('PTSans-Bold',18); c.drawString(margin+155,top-22,str(mech['difficulty']))
        c.setFont('PTSans-Bold',10.5); c.drawString(margin+14,top-50,'IMPULSES')
        iy=top-65
        for imp in mech['impulses'][:5]:
            hh=_draw_para(c,'- '+html.escape(imp),styles['body'],margin+18,iy,left_w-32); iy-=hh+1
        if iy < top-box_h+8:
            layout_errors.append('Environment impulses overflow the measured summary card.')
        if art_path.exists():
            iw,ih=_image_fit(art_path,art_w,box_h)
            c.drawImage(ImageReader(str(art_path)),art_x+(art_w-iw)/2,top-box_h+(box_h-ih)/2,width=iw,height=ih,preserveAspectRatio=True,mask='auto')
        top-=box_h+10

        fp_h=draw_fast_play(margin,top,W-2*margin); top-=fp_h+10
        if top < safe_content_bottom:
            layout_errors.append('Environment Fast Play extends below the safe printable content area.')

        if mech.get('potentialAdversaries'):
            potential=', '.join(mech['potentialAdversaries'])
            pbox_h=_measure_potential_adversaries(potential,styles,W-2*margin)
            layout_metrics['potentialAdversariesHeightPt']=pbox_h
            _draw_card(c,margin,top-pbox_h,W-2*margin,pbox_h,6,WHITE)
            c.setFillColor(PURPLE); c.setFont('PTSans-Bold',10); c.drawString(margin+10,top-17,'POTENTIAL ADVERSARIES')
            body_top=top-29
            _draw_para(c,html.escape(potential),styles['body'],margin+10,body_top,W-2*margin-20)
            top-=pbox_h+10
            if top < safe_content_bottom:
                layout_errors.append('Environment potential-adversaries box extends below the safe printable content area.')

        features=print_model['features']; fullw=W-2*margin
        # If there is not enough meaningful room for the feature heading plus at least
        # one feature, start the feature list cleanly on page 2.
        first_need=_feature_flow_height(features[:1],fullw,styles) if features else 0
        if features and top-(18+first_need) < safe_content_bottom:
            c.showPage(); base_page()
            c.setFillColor(PURPLE); c.setFont('PTSansNarrow-Bold',18); c.drawString(margin,usable_top-4,f"{ident['name'].upper()} - FEATURES")
            top=usable_top-28
        else:
            c.setFillColor(PURPLE); c.setFont('PTSansNarrow-Bold',14); c.drawString(margin,top,'FEATURES'); top-=18

        remaining=[]
        for idx,f in enumerate(features):
            need=_feature_flow_height([f],fullw,styles)
            if top-need < safe_content_bottom:
                remaining=features[idx:]
                break
            used=draw_feature_block(margin,top,fullw,f,environment=True)
            top-=used+2
        if remaining:
            # If already on page 2, a further continuation would exceed the two-page
            # contract. Otherwise use page 2 for the remainder.
            current_pages=c.getPageNumber()
            if current_pages >= 2:
                layout_errors.append('Environment feature list exceeds the supported two-page printable area.')
            else:
                c.showPage(); base_page(); c.setFillColor(PURPLE); c.setFont('PTSansNarrow-Bold',18); c.drawString(margin,usable_top-4,f"{ident['name'].upper()} - FEATURES")
                y2=usable_top-28
                for f in remaining:
                    need=_feature_flow_height([f],fullw,styles)
                    if y2-need < safe_content_bottom:
                        layout_errors.append('Environment feature continuation exceeds the supported two-page printable area.')
                        break
                    used=draw_feature_block(margin,y2,fullw,f,environment=True)
                    y2-=used+2

    c.showPage(); c.save()
    return {
        "minimumBodyFontPt": MIN_BODY_PT,
        "style": PDF_STYLE,
        "layoutErrors": layout_errors,
        "layoutWarnings": layout_warnings,
        "layoutMetrics": layout_metrics,
    }

def make_art_briefs(spec: Dict[str, Any]) -> Dict[str, Any]:
    return {k: copy.deepcopy(v) for k,v in spec.get('art',{}).items()}


def _validate_compiled_consistency(spec: Dict[str, Any], foundry: Dict[str, Any], print_model: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    ident, mech = spec["identity"], spec["mechanics"]
    if foundry.get("name") != ident["name"]:
        errors.append("Foundry name does not match canonical spec.")
    if foundry.get("flags", {}).get("cybermancy", {}).get("fastPlay") != spec["fastPlay"]:
        errors.append("Foundry flags.cybermancy.fastPlay does not match canonical spec.")
    if print_model.get("fastPlay") != spec["fastPlay"]:
        errors.append("Print model Fast Play does not match canonical spec.")
    if [f["name"] for f in print_model.get("features", [])] != [f["name"] for f in mech.get("features", [])]:
        errors.append("Print model feature order does not match canonical spec.")
    if spec["entityType"] == "adversary":
        fs = foundry.get("system", {})
        checks = [
            (fs.get("difficulty"), mech.get("difficulty"), "difficulty"),
            (fs.get("resources", {}).get("hitPoints", {}).get("max"), mech.get("hitPoints"), "HP"),
            (fs.get("resources", {}).get("stress", {}).get("max"), mech.get("stress"), "Stress"),
            (fs.get("type"), ident.get("classification"), "role"),
            (fs.get("tier"), ident.get("tier"), "tier"),
        ]
        for got, expected, label in checks:
            if got != expected:
                errors.append(f"Foundry adversary {label} does not match canonical spec.")
        if [i.get("name") for i in foundry.get("items", [])] != [f["name"] for f in mech.get("features", [])]:
            errors.append("Foundry embedded feature order/names do not match canonical spec.")
        damage = fs.get("attack", {}).get("damage", {})
        part = damage.get("main", {}) if isinstance(damage, dict) else {}
        expected_damage = mech["attack"]["damage"]
        if ("parts" in damage or damage.get("resources") != {}
                or part.get("applyTo") != "hitPoints"
                or part.get("value", {}).get("dice") != expected_damage["die"]
                or part.get("value", {}).get("flatMultiplier") != expected_damage["count"]
                or part.get("value", {}).get("bonus") != expected_damage["bonus"]
                or part.get("type") != expected_damage["types"]):
            errors.append("Foundry main attack damage does not match canonical spec.")
        fp_html = fs.get("description", "")
        if "FAST PLAY" not in fp_html:
            errors.append("Foundry adversary description is missing Fast Play.")
        custom = mech.get("attack", {}).get("damage", {}).get("customFormula")
        if custom is not None:
            compiled = fs.get("attack", {}).get("damage", {}).get("main", {}).get("value", {}).get("custom", {})
            if not compiled.get("enabled") or compiled.get("formula") != custom:
                errors.append("Foundry custom attack damage formula does not match canonical spec.")
    else:
        fs = foundry.get("system", {})
        checks = [
            (fs.get("difficulty"), mech.get("difficulty"), "difficulty"),
            (fs.get("type"), ident.get("classification"), "type"),
            (fs.get("tier"), ident.get("tier"), "tier"),
        ]
        for got, expected, label in checks:
            if got != expected:
                errors.append(f"Foundry environment {label} does not match canonical spec.")
        if "FAST PLAY" not in fs.get("description", ""):
            errors.append("Foundry environment description is missing Fast Play.")
        if [f.get("name") for f in foundry.get("items", [])] != [f["name"] for f in mech.get("features", [])]:
            errors.append("Foundry environment feature order/names do not match canonical spec.")
        if any(f.get("type") != "feature" or f.get("system", {}).get("featureForm") != feature_type_to_action_type(source["featureType"])
               for f, source in zip(foundry.get("items", []), mech.get("features", []))):
            errors.append("Foundry environment feature Items are invalid or misclassified.")
        if not isinstance(fs.get("potentialAdversaries"), dict) or "features" in fs:
            errors.append("Foundry environment uses an incompatible 2.10 data shape.")
        if foundry.get("flags", {}).get("cybermancy", {}).get("potentialAdversaryNames") != mech.get("potentialAdversaries"):
            errors.append("Foundry potential-adversary names do not match canonical spec.")
    return errors


def _validate_art(copied_assets: List[Path], spec: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    for p in copied_assets:
        if not p.exists():
            errors.append(f"Missing art asset: {p}")
            continue
        try:
            with Image.open(p) as im:
                width, height = im.size
                im.verify()
            if width < 256 or height < 256:
                errors.append(f"Art asset is below 256 px minimum: {p.name} ({width}x{height})")
        except Exception as e:
            errors.append(f"Unreadable art asset {p.name}: {e}")
    if not errors and copied_assets:
        if spec["entityType"] == "adversary":
            portrait, token = copied_assets
            with Image.open(portrait) as im: pw, ph = im.size
            with Image.open(token) as im:
                tw, th = im.size
                if im.mode not in ('RGBA', 'LA') or 'A' not in im.getbands():
                    errors.append('Adversary token must have an alpha channel.')
                else:
                    alpha = im.getchannel('A')
                    inset = max(1, min(tw, th) // 32)
                    corners = [(inset, inset), (tw - 1 - inset, inset),
                               (inset, th - 1 - inset), (tw - 1 - inset, th - 1 - inset)]
                    if any(alpha.getpixel(point) > 10 for point in corners):
                        errors.append('Adversary token must be transparent outside its outer ring.')
            if abs((pw / ph) - 0.8) > 0.08:
                warnings.append(f"Portrait aspect ratio is {pw}:{ph}; default target is 4:5.")
            if tw != th:
                errors.append("Adversary token must be square.")
            if (tw, th) != (1254, 1254):
                warnings.append(f"Token is {tw}x{th}; reference target is 1254x1254.")
        else:
            with Image.open(copied_assets[0]) as im: ew, eh = im.size
            if abs((ew / eh) - 1.5) > 0.12:
                warnings.append(f"Environment art aspect ratio is {ew}:{eh}; default target is 3:2.")
    return errors, warnings


def _validate_pdf(pdf_path: Path) -> Tuple[List[str], List[str], int]:
    errors: List[str] = []
    warnings: List[str] = []
    page_count = 0
    if not pdf_path.exists() or pdf_path.stat().st_size <= 1000:
        return ["PDF missing or empty"], warnings, page_count
    try:
        reader = PdfReader(str(pdf_path))
        page_count = len(reader.pages)
        if page_count < 1:
            errors.append("PDF has no pages.")
        if page_count > 2:
            errors.append(f"PDF has {page_count} pages; entity references support at most 2.")
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
        if "FAST PLAY" not in text:
            errors.append("PDF is missing FAST PLAY.")
        if "FEATURES" not in text:
            errors.append("PDF is missing FEATURES.")

        # Geometry/font QA uses the rendered PDF itself rather than trusting the
        # authoring coordinates. This catches clipped content and accidental font
        # reductions that text-only preflight cannot see.
        doc = fitz.open(str(pdf_path))
        for page_index, page in enumerate(doc):
            ph = float(page.rect.height); pw = float(page.rect.width)
            data = page.get_text('dict')
            for block in data.get('blocks', []):
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        txt = span.get('text', '').strip()
                        if not txt:
                            continue
                        size = float(span.get('size', 0))
                        x0,y0,x1,y1 = map(float, span.get('bbox', (0,0,0,0)))
                        if size < MIN_BODY_PT - 0.05:
                            errors.append(f"PDF page {page_index+1} contains text below {MIN_BODY_PT:.1f} pt: {txt[:48]!r} ({size:.2f} pt).")
                        if x0 < 30 or x1 > pw-30:
                            errors.append(f"PDF page {page_index+1} text crosses the horizontal safe area: {txt[:48]!r}.")
                        is_footer = txt in {'CYBERMANCY // GM REFERENCE','DAGGERHEART-COMPATIBLE HOMEBREW'}
                        if not is_footer and y1 > ph-42:
                            errors.append(f"PDF page {page_index+1} content crosses the footer safe area: {txt[:48]!r}.")
                        if y0 < 8:
                            errors.append(f"PDF page {page_index+1} content crosses the top safe area: {txt[:48]!r}.")
    except Exception as e:
        errors.append(f"PDF could not be opened or geometrically inspected: {e}")
    # Deduplicate geometry errors while preserving order.
    errors = list(dict.fromkeys(errors))
    return errors, warnings, page_count


def build_validation(spec: Dict[str, Any], schema_errors: List[str], fp_errors: List[str], fp_warnings: List[str], path_errors: List[str], foundry_path: Path, print_model_path: Path, pdf_path: Path, copied_assets: List[Path], render_meta: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    gates=[]
    a_errors=schema_errors+fp_errors+path_errors
    gates.append({"name":"A - Canonical spec","status":"pass" if not a_errors else "fail","errors":a_errors,"warnings":fp_warnings})
    mech_warnings=[]
    if spec['entityType']=='adversary' and not spec['design'].get('motivesAndTactics'):
        mech_warnings.append('Adversary has no motivesAndTactics; Fast Play behavior alignment cannot be fully reviewed.')
    if spec['entityType']=='environment' and len(spec['mechanics'].get('impulses',[]))<1:
        mech_warnings.append('Environment has no impulses.')
    gates.append({"name":"B - Mechanical design / Fast Play","status":"warning" if mech_warnings else "pass","errors":[],"warnings":mech_warnings})
    foundry_errors=[]
    foundry: Dict[str, Any] = {}
    print_model: Dict[str, Any] = {}
    try: foundry=load_json(foundry_path)
    except Exception as e: foundry_errors.append(str(e))
    try: print_model=load_json(print_model_path)
    except Exception as e: foundry_errors.append(f"Print model: {e}")
    if foundry and print_model:
        foundry_errors.extend(_validate_compiled_consistency(spec, foundry, print_model))
    gates.append({"name":"C - Foundry JSON / compiled structure","status":"pass" if not foundry_errors else "fail","errors":foundry_errors,"warnings":[]})
    cross_errors=[] if not foundry_errors else ["Compiled output consistency failed; see Gate C."]
    gates.append({"name":"D - Cross-artifact consistency","status":"pass" if not cross_errors else "fail","errors":cross_errors,"warnings":[]})
    art_errors, art_warnings=_validate_art(copied_assets,spec)
    gates.append({"name":"E - Art QA","status":"pass" if not art_errors and not art_warnings else "fail" if art_errors else "warning","errors":art_errors,"warnings":art_warnings})
    pdf_errors,pdf_warnings,page_count=_validate_pdf(pdf_path)
    if render_meta:
        pdf_errors.extend(render_meta.get('layoutErrors', []))
        pdf_warnings.extend(render_meta.get('layoutWarnings', []))
    gates.append({"name":"F - PDF QA","status":"pass" if not pdf_errors and not pdf_warnings else "fail" if pdf_errors else "warning","errors":pdf_errors,"warnings":pdf_warnings})
    statuses=[g['status'] for g in gates]
    status='fail' if 'fail' in statuses else 'warning' if 'warning' in statuses or fp_warnings else 'pass'
    return {"packageBuilderVersion":BUILDER_VERSION,"entity":spec['identity']['name'],"slug":spec['identity']['slug'],"status":status,"gates":gates,"fastPlay":{"wordCount":fast_play_word_count(spec['fastPlay']),"promptCount":len(spec['fastPlay']['prompts']),"goalPresent":bool(spec['fastPlay']['goal'])},"pdf":{"pageCount":page_count,"minimumBodyFontPt":MIN_BODY_PT,"layoutMetrics":(render_meta or {}).get('layoutMetrics',{})},"target":{"foundryCore":spec['foundry']['targetCoreVersion'],"system":f"Daggerheart {spec['foundry']['targetSystemVersion']}"}}


def build_manifest(package_root: Path, spec: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
    files=[]
    for p in sorted(package_root.rglob('*')):
        if p.is_file() and p.name != 'manifest.json':
            files.append({"path":str(p.relative_to(package_root)).replace(os.sep,'/'),"sha256":sha256_file(p),"bytes":p.stat().st_size})
    return {"packageFormat":PACKAGE_FORMAT,"packageBuilderVersion":BUILDER_VERSION,"specVersion":spec['specVersion'],"entityType":spec['entityType'],"name":spec['identity']['name'],"slug":spec['identity']['slug'],"tier":spec['identity']['tier'],"classification":spec['identity']['classification'],"validationStatus":validation['status'],"files":files}


def build(args: argparse.Namespace) -> Path:
    spec_path=Path(args.spec).resolve(); schema_path=Path(args.schema).resolve(); outdir=Path(args.output_dir).resolve()
    spec=load_json(spec_path); schema=load_json(schema_path)
    schema_errors=validate_schema(spec,schema); fp_errors,fp_warnings=validate_fast_play(spec); path_errors=validate_paths(spec)+validate_target(spec)
    if schema_errors or fp_errors or path_errors:
        for e in schema_errors+fp_errors+path_errors: print('ERROR:',e,file=sys.stderr)
        raise SystemExit(2)
    slug=spec['identity']['slug']; package_root=outdir/f'{slug}-package'
    if package_root.exists(): shutil.rmtree(package_root)
    for d in ['source/schema','foundry','print']:
        (package_root/d).mkdir(parents=True,exist_ok=True)
    # source
    spec_out=copy.deepcopy(spec); spec_out['$schema']='schema/cybermancy-entity-spec-v1.1.schema.json'
    write_json(package_root/'source'/f'{slug}.spec.json',spec_out)
    shutil.copy2(schema_path,package_root/'source/schema/cybermancy-entity-spec-v1.1.schema.json')
    write_json(package_root/'source'/f'{slug}.art-briefs.json',make_art_briefs(spec))
    print_model=compile_print_model(spec); write_json(package_root/'source'/f'{slug}.print-model.json',print_model)
    copied_assets=[]
    if spec['entityType']=='adversary':
        foundry=compile_adversary_foundry(spec,args.adversary_folder_id)
        write_json(package_root/'foundry'/f'{slug}.json',foundry)
        if not args.portrait or not args.token: raise SystemExit('Adversary build requires --portrait and --token')
        portrait_src=Path(args.portrait); token_src=Path(args.token)
        portrait_dst=package_root/'assets/images/adversaries'/f'{slug}.png'; token_dst=package_root/'assets/tokens/adversaries'/f'{slug}-token.png'
        portrait_dst.parent.mkdir(parents=True,exist_ok=True); token_dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(portrait_src,portrait_dst); shutil.copy2(token_src,token_dst); copied_assets=[portrait_dst,token_dst]
        art_for_pdf=portrait_dst
    else:
        adversary_uuids=load_json(Path(args.adversary_uuids)) if args.adversary_uuids else None
        foundry=compile_environment_foundry(spec,args.environment_folder_id,adversary_uuids)
        write_json(package_root/'foundry'/f'{slug}.json',foundry)
        if not args.environment_art: raise SystemExit('Environment build requires --environment-art')
        art_src=Path(args.environment_art); art_dst=package_root/'assets/images/environments'/f'{slug}.png'; art_dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(art_src,art_dst); copied_assets=[art_dst]; art_for_pdf=art_dst
    pdf_path=package_root/'print'/f'{slug}.pdf'; render_meta=render_pdf(spec,print_model,art_for_pdf,pdf_path)
    validation=build_validation(spec,schema_errors,fp_errors,fp_warnings,path_errors,package_root/'foundry'/f'{slug}.json',package_root/'source'/f'{slug}.print-model.json',pdf_path,copied_assets,render_meta)
    write_json(package_root/'validation.json',validation)
    manifest=build_manifest(package_root,spec,validation); write_json(package_root/'manifest.json',manifest)
    if args.zip_output:
        zip_path=Path(args.zip_output).resolve(); zip_path.parent.mkdir(parents=True,exist_ok=True)
        if zip_path.exists(): zip_path.unlink()
        with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for p in sorted(package_root.rglob('*')):
                if p.is_file(): z.write(p,arcname=str(Path(package_root.name)/p.relative_to(package_root)))
        print(zip_path)
        return zip_path
    print(package_root)
    return package_root


def validate_command(args: argparse.Namespace) -> None:
    spec=load_json(Path(args.spec)); schema=load_json(Path(args.schema))
    se=validate_schema(spec,schema); fe,fw=validate_fast_play(spec); pe=validate_paths(spec)+validate_target(spec)
    result={"status":"pass" if not(se or fe or pe) else "fail","errors":se+fe+pe,"warnings":fw,"fastPlayWordCount":fast_play_word_count(spec.get('fastPlay',{'prompts':[],'goal':''}))}
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if result['status']!='pass': raise SystemExit(2)


def main() -> None:
    ap=argparse.ArgumentParser(description='Cybermancy Package Builder v1.4.0 (Foundry 14.368 / Daggerheart 2.10.5)')
    sub=ap.add_subparsers(dest='cmd',required=True)
    b=sub.add_parser('build'); b.add_argument('--spec',required=True); b.add_argument('--schema',required=True); b.add_argument('--output-dir',required=True); b.add_argument('--portrait'); b.add_argument('--token'); b.add_argument('--environment-art'); b.add_argument('--zip-output'); b.add_argument('--adversary-folder-id',default=DEFAULT_ADVERSARY_FOLDER); b.add_argument('--environment-folder-id',default=DEFAULT_ENVIRONMENT_FOLDER); b.add_argument('--adversary-uuids',help='JSON map of exact potential-adversary names to verified Actor UUIDs'); b.set_defaults(func=build)
    v=sub.add_parser('validate'); v.add_argument('--spec',required=True); v.add_argument('--schema',required=True); v.set_defaults(func=validate_command)
    args=ap.parse_args(); args.func(args)

if __name__=='__main__': main()
