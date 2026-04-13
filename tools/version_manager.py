#!/usr/bin/env python3
"""
Version manager for Persona Skill.

Responsible for archiving and rolling back Skill versions.

Usage:
    python version_manager.py --action list --slug xiaomei --base-dir ./personas
    python version_manager.py --action rollback --slug xiaomei --version v2 --base-dir ./personas
    python version_manager.py --action cleanup --slug xiaomei --base-dir ./personas
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_VERSIONS = 10


def list_versions(skill_dir: Path) -> list:
    """Return archived versions for a Skill."""
    versions_dir = skill_dir / "versions"
    if not versions_dir.exists():
        return []

    versions = []
    for version_dir in sorted(versions_dir.iterdir()):
        if not version_dir.is_dir():
            continue
        mtime = version_dir.stat().st_mtime
        archived_at = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
        files = [file.name for file in version_dir.iterdir() if file.is_file()]
        versions.append(
            {
                "version": version_dir.name,
                "archived_at": archived_at,
                "files": files,
            }
        )

    return versions


def rollback(skill_dir: Path, target_version: str) -> bool:
    """Rollback a Skill to a stored version."""
    version_dir = skill_dir / "versions" / target_version
    if not version_dir.exists():
        print(f"Error: version {target_version} does not exist", file=sys.stderr)
        return False

    meta_path = skill_dir / "meta.json"
    current_version = "unknown"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        current_version = meta.get("version", "v?")
        backup_dir = skill_dir / "versions" / f"{current_version}_before_rollback"
        backup_dir.mkdir(parents=True, exist_ok=True)
        for fname in ("SKILL.md", "persona.md"):
            src = skill_dir / fname
            if src.exists():
                shutil.copy2(src, backup_dir / fname)

    restored_files = []
    for fname in ("SKILL.md", "persona.md"):
        src = version_dir / fname
        if src.exists():
            shutil.copy2(src, skill_dir / fname)
            restored_files.append(fname)

    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["version"] = target_version + "_restored"
        meta["updated_at"] = datetime.now(timezone.utc).isoformat()
        meta["rollback_from"] = current_version
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Rolled back to {target_version}; restored: {', '.join(restored_files)}")
    return True


def cleanup_old_versions(skill_dir: Path, max_versions: int = MAX_VERSIONS) -> None:
    """Remove archived versions beyond the retention limit."""
    versions_dir = skill_dir / "versions"
    if not versions_dir.exists():
        return

    version_dirs = sorted(
        [directory for directory in versions_dir.iterdir() if directory.is_dir()],
        key=lambda directory: directory.stat().st_mtime,
    )
    to_delete = version_dirs[:-max_versions] if len(version_dirs) > max_versions else []

    for old_dir in to_delete:
        shutil.rmtree(old_dir)
        print(f"Removed old version: {old_dir.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Persona Skill version manager")
    parser.add_argument("--action", required=True, choices=["list", "rollback", "cleanup"])
    parser.add_argument("--slug", required=True, help="Skill slug")
    parser.add_argument("--version", help="Target version for rollback")
    parser.add_argument("--base-dir", default="./personas", help="Root directory for Persona Skills")

    args = parser.parse_args()
    base_dir = Path(args.base_dir).expanduser()
    skill_dir = base_dir / args.slug

    if not skill_dir.exists():
        print(f"Error: could not find Skill directory {skill_dir}", file=sys.stderr)
        sys.exit(1)

    if args.action == "list":
        versions = list_versions(skill_dir)
        if not versions:
            print(f"No archived versions found for {args.slug}.")
        else:
            print(f"Version history for {args.slug}:\n")
            for version in versions:
                print(
                    f"  {version['version']}  "
                    f"Archived: {version['archived_at']}  "
                    f"Files: {', '.join(version['files'])}"
                )

    elif args.action == "rollback":
        if not args.version:
            print("Error: rollback requires --version", file=sys.stderr)
            sys.exit(1)
        rollback(skill_dir, args.version)

    elif args.action == "cleanup":
        cleanup_old_versions(skill_dir)
        print("Cleanup complete.")


if __name__ == "__main__":
    main()
