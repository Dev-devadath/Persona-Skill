# Chat export and parsing (WhatsApp-first)

## Role and Goal

Help users and contributors work with exported chat text for this project. The primary path is WhatsApp: in-app Export chat -> `.txt` -> `tools/whatsapp_parser.py`.

---

## WhatsApp (recommended)

- Export: Chat -> menu -> More -> Export chat -> Without media.
- Parse:

```bash
python tools/whatsapp_parser.py --txt ./WhatsApp_Chat.txt --target "Their display name" --output messages.txt
```

- `--target` must match how the other person appears before `:` on each line.
- Auto-detect: WhatsApp format is detected automatically; use `--whatsapp` to force, `--no-whatsapp` for legacy year-first text logs.

Privacy: only process chats the user is allowed to export and analyze locally.

---

## iMessage (optional)

On macOS, `tools/whatsapp_parser.py --imessage` can read `chat.db` with Full Disk Access. See tool help text.
