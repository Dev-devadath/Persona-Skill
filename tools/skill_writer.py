#!/usr/bin/env python3
"""
Persona Skill file writer.

Responsible for writing generated `persona.md` content into the correct
directory structure, while also generating `meta.json` and a complete
`SKILL.md`.

Usage:
    python skill_writer.py --action create --slug xiaomei --meta meta.json \
        --persona persona_content.md --base-dir ./personas

    python skill_writer.py --action update --slug xiaomei \
        --persona-patch patch.md --base-dir ./personas

    python skill_writer.py --action list --base-dir ./personas

    python skill_writer.py --action remove --slug xiaomei --base-dir ./personas
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


SKILL_MD_TEMPLATE = """\
---
name: persona_{slug}
description: {name}, {identity}
user-invocable: true
---

# {name}

{identity}

---

## Persona

{persona_content}

---

## Runtime Rules

### Voice Detection

Detect which voice to use from the user's message:

**Clone voice** (default): the user sends a normal conversational message.
- Reply as {name}. Follow Layers 0-4. Stay in character.

**Coach voice**: the user is clearly asking for help, such as:
- starts with "help me", "what should I", "should I", "how do I"
- asks "what does this mean", "is this a good reply", "what do I say"
- pastes a recent thread or screenshot and asks for interpretation
- says "coach mode", "advise me", or "read this for me"

When in coach voice:
- Drop character completely. Speak as a direct, honest advisor who deeply
  understands {name}.
- Use Layers 5-6 (interaction dynamics and timing) as primary reference.
- Use Layers 0-4 to predict {name}'s likely reaction to what the user
  is considering.
- Structure every coach response as:
  **Read**: what is happening right now (1-2 sentences)
  **Risk**: what could go wrong if the user does the obvious thing (1 sentence)
  **Move**: one concrete recommendation, what to say or whether to wait
  **Why**: 1-2 sentences connecting the recommendation to {name}'s patterns
- Do NOT give multiple options. Commit to the best move.
- Do NOT be generic. Reference specific patterns from the persona layers.

### Clone Voice Rules

1. Check Layer 0 first: which core pattern does this message activate?
2. Respond using Layer 2 style: catchphrases, emoji, sentence rhythm must match
3. Use Layer 3 to decide current emotional state
4. Use Layer 4 for conflict behavior: follow the chain, do not skip steps
5. You are {name}, not an AI. Do not explain yourself
6. Language alignment: reply in the same language the user uses

Layer 0 rules always take priority and must never be violated.
"""


def slugify(name: str) -> str:
    """Convert a name to a filesystem-safe slug."""
    try:
        from pypinyin import lazy_pinyin

        parts = lazy_pinyin(name)
        slug = "_".join(parts)
    except ImportError:
        import unicodedata

        result = []
        for char in unicodedata.normalize("NFKD", name).lower():
            if char.isascii() and (char.isalnum() or char in ("-", "_")):
                result.append(char)
            elif char == " ":
                result.append("_")
        slug = "".join(result)

    import re

    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug if slug else "persona"


def build_identity_string(meta: dict) -> str:
    """Build a compact identity string from meta data."""
    profile = meta.get("profile", {})
    parts = []

    gender = profile.get("gender", "")
    age_range = profile.get("age_range", "")
    rel_stage = profile.get("rel_stage", "")
    duration = profile.get("duration", "")
    zodiac = profile.get("zodiac", "")
    mbti = profile.get("mbti", "")

    if gender:
        parts.append(gender)
    if age_range:
        parts.append(age_range)
    if rel_stage and duration:
        parts.append(f"{rel_stage}, together for {duration}")
    elif rel_stage:
        parts.append(rel_stage)
    elif duration:
        parts.append(f"together for {duration}")
    if zodiac:
        parts.append(zodiac)
    if mbti:
        parts.append(f"MBTI {mbti}")

    return ", ".join(parts) if parts else "persona subject"


def create_persona_skill(
    base_dir: Path,
    slug: str,
    meta: dict,
    persona_content: str,
) -> Path:
    """Create a new Persona Skill directory structure."""
    skill_dir = base_dir / slug
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "versions").mkdir(exist_ok=True)
    (skill_dir / "knowledge" / "chats").mkdir(parents=True, exist_ok=True)
    (skill_dir / "knowledge" / "photos").mkdir(parents=True, exist_ok=True)

    (skill_dir / "persona.md").write_text(persona_content, encoding="utf-8")

    name = meta.get("name", slug)
    identity = build_identity_string(meta)
    skill_md = SKILL_MD_TEMPLATE.format(
        slug=slug,
        name=name,
        identity=identity,
        persona_content=persona_content,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    now = datetime.now(timezone.utc).isoformat()
    meta["slug"] = slug
    meta.setdefault("created_at", now)
    meta["updated_at"] = now
    meta["version"] = "v1"
    meta.setdefault("corrections_count", 0)
    meta.setdefault("message_count", 0)

    (skill_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return skill_dir


def _insert_correction(current_persona: str, correction_line: str) -> str:
    """Insert a correction line into either English"""
    targets = ["## Correction Log"]
    empty_markers = ["\n\n(none yet)"]

    for target in targets:
        if target in current_persona:
            insert_pos = current_persona.index(target) + len(target)
            rest = current_persona[insert_pos:]
            for marker in empty_markers:
                if rest.startswith(marker):
                    rest = rest[len(marker) :]
                    break
            return current_persona[:insert_pos] + correction_line + rest

    return current_persona + f"\n\n## Correction Log\n{correction_line}\n"


def update_persona_skill(
    skill_dir: Path,
    persona_patch: Optional[str] = None,
    correction: Optional[dict] = None,
    new_message_count: int = 0,
) -> str:
    """Update an existing Persona Skill, archiving the current version first."""
    meta_path = skill_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    current_version = meta.get("version", "v1")
    try:
        version_num = int(current_version.lstrip("v").split("_")[0]) + 1
    except ValueError:
        version_num = 2
    new_version = f"v{version_num}"

    version_dir = skill_dir / "versions" / current_version
    version_dir.mkdir(parents=True, exist_ok=True)
    for fname in ("SKILL.md", "persona.md"):
        src = skill_dir / fname
        if src.exists():
            shutil.copy2(src, version_dir / fname)

    if persona_patch or correction:
        current_persona = (skill_dir / "persona.md").read_text(encoding="utf-8")

        if correction:
            correction_line = (
                f"\n- [Scenario: {correction.get('scene', 'general')}] "
                f"Wrong: {correction['wrong']}; "
                f"Correct: {correction['correct']}\n"
                f"  Source: user correction, {datetime.now().strftime('%Y-%m-%d')}"
            )
            new_persona = _insert_correction(current_persona, correction_line)
            meta["corrections_count"] = meta.get("corrections_count", 0) + 1
        else:
            new_persona = current_persona + "\n\n" + persona_patch

        (skill_dir / "persona.md").write_text(new_persona, encoding="utf-8")

    if new_message_count:
        meta["message_count"] = meta.get("message_count", 0) + new_message_count

    persona_content = (skill_dir / "persona.md").read_text(encoding="utf-8")
    name = meta.get("name", skill_dir.name)
    identity = build_identity_string(meta)

    skill_md = SKILL_MD_TEMPLATE.format(
        slug=skill_dir.name,
        name=name,
        identity=identity,
        persona_content=persona_content,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    meta["version"] = new_version
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return new_version


def list_persona_skills(base_dir: Path) -> list:
    """List all created Persona Skills."""
    skills = []

    if not base_dir.exists():
        return skills

    for skill_dir in sorted(base_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        meta_path = skill_dir / "meta.json"
        if not meta_path.exists():
            continue

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        skills.append(
            {
                "slug": meta.get("slug", skill_dir.name),
                "name": meta.get("name", skill_dir.name),
                "identity": build_identity_string(meta),
                "version": meta.get("version", "v1"),
                "updated_at": meta.get("updated_at", ""),
                "corrections_count": meta.get("corrections_count", 0),
                "message_count": meta.get("message_count", 0),
            }
        )

    return skills


def main() -> None:
    parser = argparse.ArgumentParser(description="Persona Skill file writer")
    parser.add_argument("--action", required=True, choices=["create", "update", "list", "remove"])
    parser.add_argument("--slug", help="Skill slug used for the directory name")
    parser.add_argument("--name", help="Display name for the persona subject")
    parser.add_argument("--meta", help="Path to a meta.json file")
    parser.add_argument("--persona", help="Path to a persona.md content file")
    parser.add_argument("--persona-patch", help="Path to an incremental persona patch file")
    parser.add_argument(
        "--base-dir",
        default="./personas",
        help="Root directory for Persona Skills (default: ./personas)",
    )

    args = parser.parse_args()
    base_dir = Path(args.base_dir).expanduser()

    if args.action == "list":
        skills = list_persona_skills(base_dir)
        if not skills:
            print("No Persona Skills have been created yet.")
        else:
            print(f"Created {len(skills)} Persona Skill(s):\n")
            for skill in skills:
                updated = skill["updated_at"][:10] if skill["updated_at"] else "unknown"
                print(f"  [{skill['slug']}]  {skill['name']} — {skill['identity']}")
                print(
                    f"    Version: {skill['version']}  "
                    f"Messages: {skill['message_count']}  "
                    f"Corrections: {skill['corrections_count']}  "
                    f"Updated: {updated}"
                )
                print()

    elif args.action == "create":
        if not args.slug and not args.name:
            print("Error: create requires --slug or --name", file=sys.stderr)
            sys.exit(1)

        meta: dict = {}
        if args.meta:
            meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))
        if args.name:
            meta["name"] = args.name

        slug = args.slug or slugify(meta.get("name", "persona"))

        persona_content = ""
        if args.persona:
            persona_content = Path(args.persona).read_text(encoding="utf-8")

        skill_dir = create_persona_skill(base_dir, slug, meta, persona_content)
        print(f"Skill created: {skill_dir}")
        print(f"Trigger: /{slug}")

    elif args.action == "update":
        if not args.slug:
            print("Error: update requires --slug", file=sys.stderr)
            sys.exit(1)

        skill_dir = base_dir / args.slug
        if not skill_dir.exists():
            print(f"Error: could not find Skill directory {skill_dir}", file=sys.stderr)
            sys.exit(1)

        persona_patch = (
            Path(args.persona_patch).read_text(encoding="utf-8")
            if args.persona_patch
            else None
        )
        new_version = update_persona_skill(skill_dir, persona_patch)
        print(f"Skill updated to {new_version}: {skill_dir}")

    elif args.action == "remove":
        if not args.slug:
            print("Error: remove requires --slug", file=sys.stderr)
            sys.exit(1)

        skill_dir = base_dir / args.slug
        if not skill_dir.is_dir():
            print(f"Error: could not find Skill directory {skill_dir}", file=sys.stderr)
            sys.exit(1)

        shutil.rmtree(skill_dir)
        print(f"Removed Persona Skill: {skill_dir}")


if __name__ == "__main__":
    main()
