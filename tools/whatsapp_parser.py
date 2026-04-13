#!/usr/bin/env python3
"""
Chat history parser (WhatsApp export .txt primary; iMessage optional).

Supported sources:
  - WhatsApp: official "Export chat" .txt (recommended; use --txt)
  - iMessage (macOS): ~/Library/Messages/chat.db
  - Legacy generic text logs with year-first timestamps

Usage:
  python whatsapp_parser.py --txt ./WhatsApp_Chat.txt --target "Isha (Yip)" --output messages.txt
  python whatsapp_parser.py --imessage --db ~/Library/Messages/chat.db --target "+1xxxxxxxxxx" --output messages.txt
  python whatsapp_parser.py --imessage --db ~/Library/Messages/chat.db --list-contacts
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def open_db(db_path: str) -> sqlite3.Connection | None:
    """Open a SQLite database in read-only mode."""
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("SELECT name FROM sqlite_master LIMIT 1")
        return conn
    except sqlite3.DatabaseError as exc:
        print(f"Could not open database {db_path}: {exc}", file=sys.stderr)
        return None


RE_WHATSAPP_LINE_START = re.compile(
    r"^(?P<dm>\d{1,2}/\d{1,2}/\d{2,4}),\s+"
    r"(?P<clock>\d{1,2}:\d{2}(?:[\u202f\s]*)(?:AM|PM))\s+-\s+",
    re.IGNORECASE,
)


WHATSAPP_SYSTEM_MARKERS = (
    "Messages and calls are end-to-end",
    "end-to-end encrypted",
    "Messages to this chat and calls are now secured",
    "Disappearing messages",
    "You turned on disappearing",
    "You turned off disappearing",
    "changed this group's icon",
    "changed the subject",
    "created group",
    "You added",
    "You removed",
    "left the group",
    "joined using this group's invite",
    "Waiting for this message",
    "This message was deleted",
    "You deleted this message",
    "<Media omitted>",
    "Voice call",
    "Video call",
    "Missed voice call",
    "Missed video call",
)


WHATSAPP_ME_SENDERS = frozenset(
    {
        "you",
        "tu",
        "tú",
        "voce",
        "você",
    }
)


def _whatsapp_rest_is_system(rest: str) -> bool:
    text = rest.strip()
    if not text:
        return True
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in WHATSAPP_SYSTEM_MARKERS)


def _whatsapp_parse_sender_body(rest: str) -> tuple[str | None, str | None]:
    """Split a WhatsApp message into sender and body."""
    rest = rest.strip()
    if ":" not in rest:
        return None, None
    sender, body = rest.split(":", 1)
    sender = sender.strip()
    body = body.strip()
    if not sender or len(sender) > 80:
        return None, None
    if len(sender) > 50 and " " in sender[:50]:
        return None, None
    return sender, body


def looks_like_whatsapp_export(lines: list[str]) -> bool:
    """Heuristic: enough lines match the WhatsApp timestamp prefix."""
    hits = 0
    for line in lines[:120]:
        stripped = line.strip()
        if not stripped:
            continue
        if RE_WHATSAPP_LINE_START.match(stripped):
            hits += 1
            if hits >= 2:
                return True
    return hits >= 1


def parse_whatsapp_export(file_path: str, target_name: str) -> list[dict]:
    """Parse an official WhatsApp Export chat .txt file."""
    messages: list[dict] = []

    with open(file_path, "r", encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()

    target_lower = target_name.strip().lower()
    current_sender: str | None = None
    current_time: str | None = None
    pending_content_lines: list[str] = []

    def sender_to_role(sender: str) -> str:
        lowered = sender.strip().lower()
        if lowered in WHATSAPP_ME_SENDERS:
            return "me"
        if not target_lower:
            return "me"
        if target_lower in lowered or lowered in target_lower:
            return "them"
        return "me"

    def flush_pending() -> None:
        nonlocal pending_content_lines
        if not current_sender or not pending_content_lines:
            pending_content_lines = []
            return
        content = "\n".join(pending_content_lines).strip()
        pending_content_lines = []
        if not content:
            return
        messages.append(
            {
                "sender": sender_to_role(current_sender),
                "content": content,
                "timestamp": current_time or "",
                "contact_id": "",
            }
        )

    for raw in lines:
        line = raw.rstrip("\n\r")
        stripped = line.strip()
        if not stripped:
            if current_sender and pending_content_lines:
                pending_content_lines.append("")
            continue

        match = RE_WHATSAPP_LINE_START.match(stripped)
        if match:
            flush_pending()
            rest = stripped[match.end() :]
            if _whatsapp_rest_is_system(rest):
                current_sender = None
                current_time = None
                pending_content_lines = []
                continue

            sender, body = _whatsapp_parse_sender_body(rest)
            if not sender or body is None:
                current_sender = None
                current_time = None
                pending_content_lines = []
                continue

            current_sender = sender
            current_time = f"{match.group('dm')}, {match.group('clock')}"
            pending_content_lines = [body] if body else []
            continue

        if current_sender:
            pending_content_lines.append(stripped)

    flush_pending()
    return messages


def parse_txt_export(file_path: str, target_name: str) -> list[dict]:
    """Parse generic text logs with simple sender/timestamp formats."""
    messages: list[dict] = []

    with open(file_path, "r", encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()

    pattern_datetime_sender = re.compile(
        r"^(?P<time>\d{4}[-/]\d{1,2}[-/]\d{1,2}[\s\d:]+)\s+(?P<sender>.+?)[:：]\s*(?P<content>.+)$"
    )

    current_sender: str | None = None
    current_time: str | None = None
    pending_content_lines: list[str] = []

    def flush_pending() -> None:
        nonlocal pending_content_lines
        if current_sender and pending_content_lines:
            content = " ".join(pending_content_lines).strip()
            if content:
                is_target = target_name.lower() in current_sender.lower()
                messages.append(
                    {
                        "sender": "them" if is_target else "me",
                        "content": content,
                        "timestamp": current_time or "",
                        "contact_id": "",
                    }
                )
        pending_content_lines = []

    for raw in lines:
        line = raw.rstrip("\n\r")
        match = pattern_datetime_sender.match(line)
        if match:
            flush_pending()
            current_time = match.group("time").strip()
            current_sender = match.group("sender").strip()
            pending_content_lines = [match.group("content").strip()]
        elif line.strip() and current_sender:
            pending_content_lines.append(line.strip())

    flush_pending()
    return messages


def parse_chat_text_file(
    file_path: str,
    target_name: str,
    *,
    whatsapp: bool | None = None,
) -> tuple[list[dict], str]:
    """Parse a text file and auto-detect WhatsApp vs generic text exports."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()

    if whatsapp is True:
        return parse_whatsapp_export(file_path, target_name), "WhatsApp"
    if whatsapp is False:
        return parse_txt_export(file_path, target_name), "Exported text"
    if looks_like_whatsapp_export(lines):
        return parse_whatsapp_export(file_path, target_name), "WhatsApp"
    return parse_txt_export(file_path, target_name), "Exported text"


def list_imessage_contacts(db_path: str) -> list[dict]:
    """List all contacts found in the iMessage database."""
    conn = open_db(db_path)
    if not conn:
        return []

    try:
        rows = conn.execute(
            """
            SELECT DISTINCT
                h.id AS handle_id,
                COUNT(m.ROWID) AS message_count
            FROM handle h
            LEFT JOIN message m ON m.handle_id = h.ROWID
            GROUP BY h.id
            ORDER BY message_count DESC
            """
        ).fetchall()
        return [{"handle": row["handle_id"], "count": row["message_count"]} for row in rows]
    except Exception as exc:
        print(f"Failed to read iMessage contacts: {exc}", file=sys.stderr)
        return []
    finally:
        conn.close()


def extract_imessage_messages(db_path: str, target_handle: str) -> list[dict]:
    """Extract messages for a target contact from macOS iMessage chat.db."""
    conn = open_db(db_path)
    if not conn:
        return []

    apple_epoch_offset = 978307200
    messages: list[dict] = []

    try:
        handle_rows = conn.execute(
            "SELECT ROWID, id FROM handle WHERE id LIKE ?",
            (f"%{target_handle}%",),
        ).fetchall()

        if not handle_rows:
            print(f"Could not find '{target_handle}'. Use --list-contacts to inspect all contacts.", file=sys.stderr)
            return []

        handle_ids = [row["ROWID"] for row in handle_rows]
        matched_handle = handle_rows[0]["id"]
        placeholders = ",".join("?" * len(handle_ids))
        rows = conn.execute(
            f"""
            SELECT
                m.ROWID,
                m.text,
                m.is_from_me,
                m.date,
                h.id AS handle_id
            FROM message m
            LEFT JOIN handle h ON h.ROWID = m.handle_id
            WHERE m.handle_id IN ({placeholders})
               OR (m.is_from_me = 1 AND m.ROWID IN (
                   SELECT message_id FROM chat_message_join
                   WHERE chat_id IN (
                       SELECT chat_id FROM chat_handle_join
                       WHERE handle_id IN ({placeholders})
                   )
               ))
            ORDER BY m.date ASC
            """,
            handle_ids + handle_ids,
        ).fetchall()

        for row in rows:
            text = row["text"] or ""
            if not text.strip() or text.startswith("\ufffc"):
                continue

            raw_date = row["date"] or 0
            if raw_date > 1e12:
                unix_ts = raw_date / 1e9 + apple_epoch_offset
            else:
                unix_ts = raw_date + apple_epoch_offset

            try:
                timestamp = datetime.fromtimestamp(unix_ts).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                timestamp = str(raw_date)

            messages.append(
                {
                    "sender": "me" if row["is_from_me"] else "them",
                    "content": text.strip(),
                    "timestamp": timestamp,
                    "contact_id": row["handle_id"] or matched_handle,
                }
            )

    except Exception as exc:
        print(f"Failed to read iMessage messages: {exc}", file=sys.stderr)
    finally:
        conn.close()

    return messages


CONFLICT_KEYWORDS = [
    # English
    "break up", "breakup", "i'm done", "we're done", "leave me alone",
    "i'm sorry", "sorry", "i was wrong", "stop texting", "don't text",
    "stop messaging", "blocked", "unfollow", "whatever", "fine", "nevermind",
    "forget it", "idc", "idgaf", "k.", "ok.", "fuck you", "fuck off",
    "hate you", "hate this", "so done", "over it", "toxic", "gaslight",
    "ghosting", "ghosted", "cheated", "lying", "liar", "trust issues",
    "fighting", "argument", "upset", "angry", "hurt", "crying", "mad at you",
    "annoyed", "frustrated", "not talking", "need space", "break", "split",
    # Manglish
    "deshyam", "sankadam", "poda", "thendi", "venda", "mindanda", "mathi",
    "shokam", "verupikkalle", "poytharuthu", "poti", "theppu",
    "pani aavum", "karayua", "kshemikku", "vidu", "odiko",
    "veruppitta", "veruppikkal", "veshamam"
]


SWEET_KEYWORDS = [
    # English
    "miss you", "love you", "i love", "ily", "luv u", "good morning",
    "good night", "gm", "gn", "thinking of you", "how are you", "u ok",
    "are you okay", "cute", "sweet", "bae", "babe", "baby",
    "made me think of you", "can't stop thinking", "wanna see you",
    "heart", "xoxo", "hug", "kiss", "proud of you", "love this",
    # Manglish
    "muthe", "chakkare", "ishtam", "snehikkunnu", "miss cheyyunnu",
    "food kazhicho", "kazhicho", "evideya", "kidanno", "urangiyo",
    "santhosham", "umma", "umme", "ponne", "karle", "kutta", "kutti",
    "entho cheyyuva", "entho cheyyunn"
]


def classify_messages(messages: list[dict], target_name: str = "them") -> dict:
    """Classify messages into long, conflict, sweet, and daily categories."""
    their_messages = [message for message in messages if message["sender"] == "them"]
    long_msgs = []
    conflict_msgs = []
    sweet_msgs = []
    daily_msgs = []

    for message in their_messages:
        content = message["content"]
        lowered = content.lower()
        if len(content) > 50:
            long_msgs.append(message)
        elif any(keyword.lower() in lowered for keyword in CONFLICT_KEYWORDS):
            conflict_msgs.append(message)
        elif any(keyword.lower() in lowered for keyword in SWEET_KEYWORDS):
            sweet_msgs.append(message)
        else:
            daily_msgs.append(message)

    return {
        "long_messages": long_msgs,
        "conflict_messages": conflict_msgs,
        "sweet_messages": sweet_msgs,
        "daily_messages": daily_msgs,
        "total_their_count": len(their_messages),
        "total_count": len(messages),
        "all_messages": messages,
    }


def format_output(target_name: str, classified: dict, include_context: bool = True, source: str = "Chat") -> str:
    """Format extracted content for downstream analysis."""
    lines = [
        f"# {source} Chat Extraction Result",
        f"Target: {target_name}",
        f"Messages sent by them: {classified['total_their_count']}",
        f"Total messages in conversation: {classified['total_count']}",
        "",
        "---",
        "",
        "## Long Messages (>50 chars, highest weight: viewpoints / emotion / explanation)",
        "",
    ]

    for message in classified["long_messages"]:
        ts = f"[{message['timestamp']}] " if message.get("timestamp") else ""
        lines.append(f"{ts}{message['content']}")
        lines.append("")

    lines += [
        "---",
        "",
        "## Conflict / Emotion Messages (arguments / apology / breakup / shutdown-related)",
        "",
    ]

    for message in classified["conflict_messages"]:
        ts = f"[{message['timestamp']}] " if message.get("timestamp") else ""
        lines.append(f"{ts}{message['content']}")
        lines.append("")

    lines += [
        "---",
        "",
        "## Sweet Messages (confession / missing them / daily care)",
        "",
    ]

    for message in classified["sweet_messages"]:
        ts = f"[{message['timestamp']}] " if message.get("timestamp") else ""
        lines.append(f"{ts}{message['content']}")
        lines.append("")

    lines += [
        "---",
        "",
        f"## Daily Small Talk (style reference, {len(classified['daily_messages'])} total, fully included)",
        "",
    ]

    for message in classified["daily_messages"]:
        ts = f"[{message['timestamp']}] " if message.get("timestamp") else ""
        lines.append(f"{ts}{message['content']}")

    if include_context:
        all_messages = classified["all_messages"]
        lines += [
            "",
            "---",
            "",
            f"## Full Conversation ({len(all_messages)} messages, chronological, fully included)",
            "(Format: [time] sender: content)",
            "",
        ]
        for message in all_messages:
            sender_label = target_name if message["sender"] == "them" else "me"
            ts = f"[{message['timestamp']}] " if message.get("timestamp") else ""
            lines.append(f"{ts}{sender_label}: {message['content']}")

    return "\n".join(lines)


def print_contact_list(contacts: list[dict]) -> None:
    """Print a human-readable iMessage contact list."""
    if not contacts:
        print("No contact data found.")
        return
    print(f"Found {len(contacts)} iMessage contact(s):\n")
    print(f"{'Handle (phone / Apple ID)':<45} {'Messages':<10}")
    print("-" * 55)
    for contact in contacts:
        print(f"{contact['handle']:<45} {contact['count']:<10}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chat history parser (WhatsApp .txt, iMessage, generic text)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python whatsapp_parser.py --txt ./WhatsApp_Chat.txt --target "Isha (Yip)" --output messages.txt
  python whatsapp_parser.py --txt ./chat.txt --target "Zhimin Liu" --no-whatsapp --output messages.txt
  python whatsapp_parser.py --imessage --db ~/Library/Messages/chat.db --list-contacts
  python whatsapp_parser.py --imessage --db ~/Library/Messages/chat.db --target "+1xxxxxxxxxx" --output messages.txt
        """,
    )
    parser.add_argument("--txt", help="Exported text file (WhatsApp export .txt or generic log)")
    parser.add_argument("--imessage", action="store_true", help="Use iMessage mode (macOS chat.db)")
    parser.add_argument("--db", help="iMessage database path")
    parser.add_argument("--target", help="Other person's display name or iMessage handle")
    parser.add_argument("--output", default=None, help="Output file path (defaults to stdout)")
    parser.add_argument("--list-contacts", action="store_true", help="List iMessage contacts")
    parser.add_argument("--no-context", action="store_true", help="Omit the full conversation context section")
    parser.add_argument("--json", action="store_true", help="Output raw messages as JSON")
    parser.add_argument("--whatsapp", action="store_true", help="Treat --txt as a WhatsApp export")
    parser.add_argument("--no-whatsapp", action="store_true", help="Treat --txt as a generic text export")

    args = parser.parse_args()

    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if args.whatsapp and args.no_whatsapp:
        print("Error: use only one of --whatsapp or --no-whatsapp.", file=sys.stderr)
        sys.exit(1)

    source_label = "iMessage" if args.imessage else "WhatsApp"
    messages: list[dict] = []

    if args.imessage:
        if not args.db:
            default_path = Path.home() / "Library" / "Messages" / "chat.db"
            if default_path.exists():
                args.db = str(default_path)
                print(f"Using default iMessage database: {args.db}")
            else:
                print("Error: iMessage database not found. Use --db to specify the path.", file=sys.stderr)
                print("Default path: ~/Library/Messages/chat.db", file=sys.stderr)
                print("Note: Terminal needs Full Disk Access on macOS.", file=sys.stderr)
                sys.exit(1)

        if args.list_contacts:
            print_contact_list(list_imessage_contacts(args.db))
            return

        if not args.target:
            print("Error: please provide --target (phone number or Apple ID).", file=sys.stderr)
            sys.exit(1)

        print(f"Extracting from iMessage database: {args.db}")
        messages = extract_imessage_messages(args.db, args.target)
    else:
        if not args.txt:
            print("Error: provide --txt, or use --imessage for iMessage mode.", file=sys.stderr)
            sys.exit(1)
        if not args.target:
            print("Error: please provide --target (target contact name).", file=sys.stderr)
            sys.exit(1)

        whatsapp_mode: bool | None = None
        if args.whatsapp:
            whatsapp_mode = True
        elif args.no_whatsapp:
            whatsapp_mode = False

        print(f"Parsing from text export: {args.txt}")
        messages, source_label = parse_chat_text_file(args.txt, args.target, whatsapp=whatsapp_mode)
        print(f"Detected / using format: {source_label}")

    if not messages:
        print("Warning: no messages found.", file=sys.stderr)
        if args.txt:
            print("Tips for text exports:", file=sys.stderr)
            print("  WhatsApp: --target must match the other person's display name before ':'.", file=sys.stderr)
            print("  Try --whatsapp or --no-whatsapp if auto-detection picked the wrong parser.", file=sys.stderr)
        sys.exit(1)

    their_count = sum(1 for message in messages if message["sender"] == "them")
    print(f"\nExtraction complete: {len(messages)} total messages, {their_count} sent by the target person.")

    if their_count < 200:
        print(
            f"Warning: only {their_count} messages were sent by the target person; "
            "the sample is limited and persona confidence is lower.",
            file=sys.stderr,
        )

    if args.json:
        output_content = json.dumps(messages, ensure_ascii=False, indent=2)
    else:
        classified = classify_messages(messages, args.target or "them")
        output_content = format_output(
            args.target or "them",
            classified,
            include_context=not args.no_context,
            source=source_label,
        )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(output_content)
        print(f"Wrote output to: {args.output}")
    else:
        print(output_content)


if __name__ == "__main__":
    main()
