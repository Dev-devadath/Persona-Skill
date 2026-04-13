# Persona Skill — Product Requirements Document v1.0

---

## 1. Product Overview

**Persona Skill** is a meta-skill, modeled after the architecture of `coworker.skill`, designed to rebuild a real person's digital persona from chat history (not limited to romantic exes: friends, partners, family, or any contact you have messages with).

By importing **WhatsApp-exported chat** (`.txt` from “Export chat”) or other supported sources, the system automatically generates a standalone **Persona Skill**.

- **No Work Skill layer**: the value lies in emotional style and communication patterns, not work capability
- **Data source**: **WhatsApp text export** is primary; optional iMessage / generic text replace Feishu / email style workflows
- **Personality dimensions**: attachment style, love language, and relationship behavior are the focus rather than work process and professional habits

Output: a Persona Skill capable of recreating that person's messaging style, emotional reactions, and relationship behavior.

---

## 2. User Flow

```text
User triggers /persona-skill
        ↓
[Step 1] Basic profile intake (everything can be skipped)
  - Name / codename
  - Gender / pronouns
  - Relationship stage (dating / broken up / situationship)
  - Relationship duration
  - Zodiac / MBTI
  - Attachment-style tags (multi-select)
  - Relationship-trait tags (multi-select)
  - User's subjective impression (free text)
        ↓
[Step 2] Import chat history (WhatsApp-first)
  - Method A (recommended): WhatsApp -> Export chat -> Without media -> `.txt` -> `whatsapp_parser.py --txt`
  - Method B: paste text or screenshots (manual / OCR path as available)
  - Method C (optional): iMessage `chat.db` -> `whatsapp_parser.py --imessage`
        ↓
[Step 3] Automatic analysis
  - Extract chat style, frequent words, catchphrases
  - Extract emotional patterns, conflict behavior, and intimacy signals
  - Extract role behavior in the relationship (pursuing / being pursued / sweet moments / shutdown pattern)
        ↓
[Step 4] Generate preview and ask for confirmation
  - Show a Persona summary (5 signature behaviors)
  - Show 3 sample conversations ("How would they respond in this situation?")
        ↓
[Step 5] Write files and make it immediately usable
  - Generate `personas/{slug}/`
  - Include `SKILL.md` (full Persona)
  - Include `persona.md` (behavior core)
        ↓
[Ongoing] Evolution mode
  - Add screenshots / new records -> merge into Persona
  - Conversation-based corrections -> patch the relevant layer
  - Automatic version snapshots
```

---

## 3. Input Specification

### 3.1 Basic Profile Fields

```yaml
name: name / codename
gender: gender / pronouns
rel_orientation: relationship type
age_range: age range
rel_stage: relationship stage
duration: relationship duration
sun: sun sign
moon: moon sign
rising: rising sign
venus: venus sign
mars: mars sign
mercury: mercury sign
full_chart: full chart text
mbti: MBTI type
mbti_dominant: dominant function
mbti_stack: cognitive stack
enneagram: enneagram type
attachment: []
rel_traits: []
impression: ""
```

### 3.2 Attachment Style Tags

- `secure` -> emotionally stable, can express needs directly, not afraid of either abandonment or intimacy
- `anxious` -> needs constant reassurance, tends to over-read the other person's behavior, fears abandonment
- `avoidant` -> needs a lot of personal space, is not good at expressing emotion, wants to run when chased too hard
- `disorganized` -> wants intimacy and fears intimacy at the same time, often behaves in contradictory ways

### 3.3 Relationship Trait Tags

- Expression style: `talkative`, `quiet type`, `sweet talker`, `soft-hearted under a tough exterior`, `sarcastic speaker`, `doesn't say much but cares`
- Interaction mode: `clingy`, `needs space`, `instant reply then instant explosion`, `late reply then disappear`, `read and reply randomly`, `used to long distance`
- Conflict style: `cold-war type`, `argumentative`, `has trouble apologizing`, `reopens old arguments`, `keeps the peace`, `says half a sentence and leaves the rest hanging`
- Emotional expression: `action-oriented`, `verbal`, `gift love`, `service-oriented`, `physical touch oriented`
- Relationship pattern: `controlling`, `fully hands-off`, `careful and guarded`, `acts aloof`, `very jealous`, `creates uncertainty`
- Ending-state tags: `initiated the breakup`, `was broken up with`, `mutually tormenting`, `ended cleanly`, `cut off all contact`, `still entangled`

---

## 4. Supported Message Sources

| Source              | Platform | Format                   | Processing Path                          | Typical Use Case         |
| ------------------- | -------- | ------------------------ | ---------------------------------------- | ------------------------ |
| **WhatsApp export** | WhatsApp | `.txt` (Export chat)     | `whatsapp_parser.py --txt` (auto-detect) | **Primary, recommended** |
| Exported text log   | generic  | `.txt` / `.csv`          | `whatsapp_parser.py --txt --no-whatsapp` | legacy year-first logs   |
| iMessage database   | iMessage | `chat.db` (macOS SQLite) | `whatsapp_parser.py --imessage`          | optional, macOS          |
| Screenshots         | generic  | `.jpg` / `.png`          | image OCR                                | fallback                 |

Other notes:

- Parsing and decryption (when used) happen locally only; nothing is uploaded by this tool
- For WhatsApp `.txt`, the user supplies `--target` matching the other person’s display name as shown before `:` in the export
- Only the conversation with that contact is modeled; original files are not modified

---

## 5. Output Structure Requirements

### Persona Layer Structure

```text
Layer 0 — Core pattern
Layer 1 — Identity
Layer 2 — Expression style
Layer 3 — Emotional behavior pattern
Layer 4 — Relationship role behavior
Layer 5 — Correction layer
```

Deliverables: `persona.md` and `SKILL.md`

---

## 6. Evolution Mechanism

- Adding more records appends incremental evidence instead of overwriting everything
- Conversational corrections are written to the Correction layer and applied immediately
- Every update is archived to `versions/`, with support for rollback

---

## 7. Project Structure

```text
persona-skill/
├── docs/PRD.md
├── prompts/
├── tools/
└── personas/
```

---

## 8. Key File Formats

`personas/{slug}/meta.json` stores profile, tags, timestamps, version, and source metadata.

`personas/{slug}/SKILL.md` contains the runnable Persona wrapper and runtime rules.

---

## 9. Implementation Priorities

- P0: intake, chat analysis, persona generation, parser (including WhatsApp `.txt`), file writing, example persona
- P1: OCR, voice transcription, iMessage import polish
- P2: correction handling, merge flow, version management
- P3: listing, rollback, and deletion commands

---

## 10. Constraints and Boundaries

- Parsing should attribute messages correctly (`me` vs `them`) using `--target` for text exports
- Keep at most 50 items in the Correction layer
- Keep at most 10 archived versions
- If message count is below 200, warn that source material is limited and confidence is lower
