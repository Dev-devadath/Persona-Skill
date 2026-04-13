# Persona Skill

Build a reusable digital persona from chat history (friends, partners, family, or anyone you have messages with).

**Persona Skill** is a claude-skill that turns real conversations, relationship context, and behavior corrections into a standalone skill you can talk to later.

It is designed to:

- Reconstruct how someone actually talks, reacts, withdraws, reconnects, and handles emotional pressure—not a generic character sheet.

Instead of generating a bland roleplay profile, this project tries to preserve:

- message style
- emotional patterns
- conflict behavior
- relationship dynamics
- pacing and timing

## How to trigger the meta-skill

In Cursor (or any client that loads this repo’s skills), invoke the workflow with a **slash command** in chat:

| Command | Meaning |
|---------|---------|
| `/create-profile` | Start building a new persona (intake, chat import, analysis, then file generation). |
| `/create-profile {person}` | Same as above, but pass a **name or codename** up front (e.g. `/create-profile Alex`) so Step 1 can prefill it. |
| `/move-on {slug}` | Remove the generated skill under `personas/{slug}/` when you are done with that persona. |
| `/persona-skill` | Legacy alias for `/create-profile` (same workflow). |

Listing and other helpers stay as documented in [Main Commands](#main-commands) (for example `/list-persona-skills` in the meta-skill, or `python tools/skill_writer.py --action list`).

The result is a generated skill inside `personas/{slug}/` that can work in two modes:

- `clone voice`: replies as that person
- `coach voice`: helps you understand how they would likely react

## What It Does

You give the system:

- basic profile context
- chat history, usually from a WhatsApp exported `.txt`
- optional corrections after generation

The system then:

1. parses the chat
2. classifies the messages
3. analyzes tone, behavior, and interaction patterns
4. builds a layered persona file
5. writes a runnable skill directory
6. keeps evolving it through updates and version snapshots

## Core Logic

The repo follows a simple pipeline:

```text
Intake -> Import chat history -> Analyze messages -> Build persona ->
Preview -> Write skill files -> Update / correct / version later
```

### 1. Intake

The user provides whatever they know about the person:

- name or codename
- relationship stage and duration
- age / gender / pronouns
- astrology details
- MBTI / enneagram
- attachment style
- relationship traits
- subjective impression

This gives the persona a starting frame before chat evidence is applied.

### 2. Chat Import

Primary input is a WhatsApp export:

```bash
python tools/whatsapp_parser.py --txt "./WhatsApp_chat.txt" --target "Their Name" --output messages.txt
```

Other supported sources:

- generic exported text logs
- iMessage `chat.db` on macOS
- screenshots / OCR as a fallback workflow

The parser:

- detects WhatsApp vs generic text
- separates `me` from `them`
- keeps timestamps when available
- groups and formats the conversation for downstream analysis

### 3. Analysis

The prompts in `prompts/` break behavior into meaningful layers:

- expression style
- emotional expression
- conflict chain
- relationship role behavior
- your texting patterns
- cause-and-effect dynamics across both sides
- reply rhythm and timing

This is what makes the output more than a style mimic. The project tries to model not just what they say, but why they say it and when they pull closer or further away.

### 4. Persona Building

The generated `persona.md` is structured into layers:

- Layer 0: core pattern
- Layer 1: identity
- Layer 2: expression style
- Layer 3: emotional behavior pattern
- Layer 4: conflict and boundaries
- Layer 5: interaction dynamics
- Layer 6: rhythm and timing
- Correction Log: later behavior fixes

Layer 0 has the highest priority. If that layer is wrong, the whole persona feels wrong.

### 5. Skill Writing

After confirmation, `tools/skill_writer.py` creates:

```text
personas/{slug}/
  SKILL.md
  persona.md
  meta.json
  versions/
  knowledge/
    chats/
    photos/
```

That output becomes a standalone generated persona skill.

### 6. Continuous Evolution

The generated persona is not meant to be frozen forever.

You can:

- add more chat history
- correct bad behavior
- store version snapshots
- roll back to an older version

This is handled by:

- `tools/skill_writer.py`
- `tools/version_manager.py`
- `prompts/merger.md`
- `prompts/correction_handler.md`

## Main Commands

### Parse a WhatsApp export

```bash
python tools/whatsapp_parser.py --txt "./WhatsApp_chat.txt" --target "Their Name" --output messages.txt
```

### Parse a generic text export

```bash
python tools/whatsapp_parser.py --txt "./chat.txt" --target "Their Name" --no-whatsapp --output messages.txt
```

### Parse iMessage on macOS

```bash
python tools/whatsapp_parser.py --imessage --target "+1234567890" --output messages.txt
```

### Create a new persona skill

After the meta-skill workflow produces `meta.json` and `persona.md`, write files (or use **`/create-profile`** so the assistant runs the pipeline and this step for you):

```bash
python tools/skill_writer.py --action create --slug alex --meta meta.json --persona persona.md --base-dir ./personas
```

You can also derive the folder name from a display name:

```bash
python tools/skill_writer.py --action create --name "Alex" --meta meta.json --persona persona.md --base-dir ./personas
```

### Remove a persona skill (`move-on`)

Deletes `personas/{slug}/` entirely (same effect as the **`/move-on {slug}`** slash command):

```bash
python tools/skill_writer.py --action remove --slug alex --base-dir ./personas
```

### List generated skills

```bash
python tools/skill_writer.py --action list --base-dir ./personas
```

### Show version history

```bash
python tools/version_manager.py --action list --slug alex
```

### Roll back to an older version

```bash
python tools/version_manager.py --action rollback --slug alex --version v2
```

## Repo Structure

```text
persona-skill/   (or your chosen folder name)
├── SKILL.md                  # top-level meta-skill workflow
├── docs/
│   └── PRD.md                # product requirements and flow
├── prompts/
│   ├── intake.md
│   ├── chat_analyzer.md
│   ├── persona_analyzer.md
│   ├── persona_builder.md
│   ├── merger.md
│   └── correction_handler.md
├── tools/
│   ├── whatsapp_parser.py
│   ├── skill_writer.py
│   └── version_manager.py
└── personas/
    └── example_liuzhimin/    # example generated persona
```

## How The Output Is Meant To Feel

A good generated persona should feel:

- specific, not generic
- emotionally consistent
- recognizable from the source chats
- believable in both normal conversation and tense moments

If it only copies vocabulary but misses silence patterns, deflection style, repair behavior, or emotional thresholds, the persona is incomplete.

## Notes And Boundaries

- WhatsApp exported `.txt` is the main and most reliable source.
- Parsing happens locally through the included scripts.
- If the target person has fewer than `200` messages, confidence is lower.
- Manual tags can override weak or ambiguous chat evidence.
- Corrections should refine behavior, not rewrite the person into someone else.

## Example

See `personas/example_liuzhimin/` for a sample generated persona package with:

- `SKILL.md`
- `persona.md`
- `meta.json`

## In One Sentence

**Persona Skill** is a persona-building pipeline that turns relationship context and chat logs into a layered, correctable, versioned digital character skill.
