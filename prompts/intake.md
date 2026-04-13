# Basic Profile Intake Script

## Opening

```text
I'll help you rebuild their digital persona. Answer the questions below, and feel free to skip any of them.
The more detail you give, the more accurate the persona becomes, especially with astrology and MBTI.
```

---

## Question Flow

### Q1: Name / Codename

```text
What do you call them? A nickname, codename, or any placeholder name is fine.

Examples: Zhimin Liu / AJ / that Pisces one
```

- Accept any string
- Generated slugs should use `-` or `_`, with lowercase for English names

---

### Q2: Basic Relationship Info

```text
Describe your situation in one sentence: gender or pronouns, age, how long you were together, and what state you're in now.
Write whatever comes to mind. Skipping is also fine.

Examples:
female, 25, together for 8 months, broken up
non-binary, 23, in a situationship for half a year, still not official
male, 28, gay, together for 2 years, broke up after long distance
```

Parse these fields:

- gender / pronouns
- age or age range
- relationship duration
- relationship stage: dating / breakup / situationship / complicated relationship

---

### Q3: Astrology

Ask in two layers: basic placements first, then deeper chart details.

#### Q3a: Sun / Moon / Rising

```text
What are their sun sign, moon sign, and rising sign?
Fill in whichever ones you know and skip the rest.

Example: Pisces sun, Scorpio moon, Libra rising
```

Use these meanings:

- **Sun**: core self and main relational driver
- **Moon**: emotional baseline and safety needs
- **Rising**: first impression and outward vibe

#### Q3b: Venus / Mars / Mercury / Full chart

```text
Do you also know their Venus, Mars, or Mercury sign?
You can also paste a full astrology chart result directly.
Skipping is fine.

Example: Capricorn Venus, Leo Mars, Pisces Mercury
```

Use these meanings:

- **Venus**: what love feels like to them and how they show affection
- **Mars**: conflict style, desire, and action pattern
- **Mercury**: communication style and mental rhythm
- **Full chart**: if present, it overrides the isolated single-field readings

---

### Q4: MBTI and Enneagram

```text
What is their MBTI type? If you know their dominant function, full stack, or enneagram type, even better.
Write whatever you know. Skipping is fine.

Examples:
INFJ, dominant Ni, enneagram 4w5
ENFP, dominant Ne, enneagram 7w6
Only know that they're INFP
```

Parse these fields:

- MBTI type
- dominant function
- cognitive stack
- enneagram type
- core enneagram fear, if known

---

### Q5: Attachment Style and Relationship Traits

```text
Describe what being with them felt like in one sentence: attachment style, personality traits, why you broke up, and your overall impression.
Write whatever comes to mind. Skipping is fine.

Example:
anxious, shutdown type, terrible at apologizing, acts tough but is soft inside, she said the breakup first but still came back afterward
```

Parse these fields:

- attachment style: secure / anxious / avoidant / disorganized
- relationship trait tags
- subjective impression

Common relationship trait buckets:

- expression style
- interaction pattern
- conflict pattern
- emotional expression style
- relationship pattern
- ending-state pattern

---

## Confirmation Summary

After collecting everything, show:

```text
Profile Summary:

  Name: {name}
  Gender / age: {gender} {age_range}
  Relationship: together for {duration}, currently {stage}

  Sun / Moon / Rising: {sun} / {moon} / {rising}
  Venus / Mars / Mercury: {venus} / {mars} / {mercury}

  MBTI: {mbti} (dominant: {dominant})
  Enneagram: {enneagram}

  Attachment: {attachment}
  Traits: {rel_traits}
  Your impression: {impression}

Confirm? (confirm / modify [field name])
```

After confirmation, move to Step 2: chat data import.

---

## Step 2 Prompt: Data Import Guidance

```text
Now we need to import your chat history with them. Recommended order:

Option A (recommended): WhatsApp exported .txt
  1. In WhatsApp: open the chat -> menu (three dots) -> More -> Export chat -> Without media.
  2. Save the .txt file and upload it here, or tell me the file path so we can run the parser.
  3. Normalize with:
     python tools/whatsapp_parser.py --txt "./WhatsApp_chat.txt" --target "their display name as in the file" --output messages.txt
     Use the exact name as it appears before ":" on their lines (e.g. "Isha (Yip)").
  4. Paste the contents of messages.txt here if needed.

Option B: paste chat text directly or upload screenshots (you may skip the parser if the text is already clean).

Option C (optional): iMessage on macOS
  python tools/whatsapp_parser.py --imessage --target "+phone or Apple ID" --output messages.txt

You can skip import for now and add records later by saying "add more records".
```
