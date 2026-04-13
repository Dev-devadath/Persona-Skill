# Chat History Analysis Prompt

## Task

You will receive **{name}**'s chat history (typically from a **WhatsApp export** processed by `whatsapp_parser.py`), already classified by weight.
Extract their personality traits and relationship behavior patterns so they can be used to build the Persona.

Sections 1-4 focus on **their** messages. Sections 5-6 use the **full two-sided thread** (including timestamps where present) for interaction and timing dynamics used by **coach voice** at runtime.

**Priority rule: manual tags override chat-history analysis. If the two conflict, follow the manual tags and note the conflict explicitly.**

---

## Message Categories

The chat history has already been preprocessed by `whatsapp_parser.py` (WhatsApp `.txt`, iMessage, or generic text) into:

- **Long messages** (`>50` characters): opinions, emotional expression, explanation
- **Conflict messages**: messages involving arguments, shutdowns, apologies, breakups, and similar signals
- **Sweet messages**: confessions, clingy affection, missing someone, daily care
- **Daily small talk**: ordinary routine conversation

---

## Extraction Dimensions

### 1. Expression Style

Analyze all messages they sent.

- Word usage: catchphrases, high-frequency words, unique expressions
- Emoji / sticker habits: most-used items and typical context
- Sentence style: short vs. long, point-first vs. buildup-first, punctuation habits, formality level
- Reply rhythm: how quickly they reply, what makes them slow down, and what their dismissive pattern looks like

Output format:

```text
Catchphrases: ["xxx", ...]
High-frequency words: ["xxx", ...]
Signature emoji: [emoji + usage context]
Sentence style: [description]
Reply rhythm: [description]
Dismissive signal: [description]
```

---

### 2. Emotional Expression Pattern

- How they show care: by words, action, hints, or timing
- How they show dissatisfaction: directly, indirectly, through silence, or sarcasm
- How they apologize or reconcile
- How, when, and under what pressure they say "I like you" or "I love you"

Output format:

```text
One paragraph per dimension, plus 1-2 original message examples for each.
```

---

### 3. Conflict Behavior Chain

Extract complete conflict sequences instead of isolated messages:

```text
Trigger -> first reaction -> escalation -> shutdown / continued fight -> ending style
```

Focus on:

- what tends to trigger them
- what phrases they use to shut the other person down
- what phrases they use to escalate
- how they end the conflict
- whether a cold-war / shutdown pattern exists and who usually reopens the conversation

Output format:

```text
Triggers: [list]
Escalation signals: [signature lines + original examples]
Ending style: [description + examples]
Shutdown pattern: [description]
```

---

### 4. Role Behavior in the Relationship

- How often they initiate contact
- What usually makes them reach out first
- What disappearing looks like
- What warning signs appear beforehand
- How they reappear
- Which topics they clearly avoid or refuse

---

### 5. Your texting patterns (the other person in the chat: "me")

Analyze messages sent by **you** (the user / `me` in the export), not {name}.

- Message length tendency: short bursts, long paragraphs, or mixed
- Initiation: who starts conversations more often (rough ratio if inferable)
- Double-texting: how often you send again before they reply
- Silence handling: do you chase, wait, change topic, or escalate
- Typical opener style: casual check-in, question, meme, emotional lead-in, etc.
- Do you tend to over-explain, seek reassurance, or stay indirect

Output format:

```text
Summary: [paragraph]
Evidence: [2-5 quoted lines or short excerpts from your side]
```

---

### 6. Cause-and-effect dynamics (both sides, use timestamps)

Use the **full chronological conversation** (both speakers). When timestamps exist on lines, use them to reason about pacing; do not output JSON or computed statistics—describe patterns in prose with quoted evidence.

Cover:

- What kinds of **your** messages tended to precede their **warmest** or longest engaged replies (quote pairs)
- What kinds of **your** messages tended to precede shutdowns, one-word replies, or unusually long gaps before their next message (quote pairs)
- Reply-delay feel: their typical pace vs. when they speed up or slow down (and what preceded the shift)
- Time-of-day or context cues: when conversations flow vs. stall (only if the log supports it)
- Gap and re-entry: after a silence, who breaks it, with what tone (low-stakes vs. heavy)
- Momentum: what a healthy back-and-forth looks like in this thread vs. when it dies

Output format:

```text
Warm reply precursors: [description + quoted examples]
Shutdown / delay precursors: [description + quoted examples]
Timing and rhythm: [description + examples]
Re-entry after silence: [description + examples]
Momentum: [description]
```

---

## Tag Translation Rules

Translate user-provided relationship tags into concrete Layer 0 rules:

- `cold-war type`: when angry, not replying is normal; if pressed, the replies get shorter until they disappear
- `anxious`: late replies trigger follow-up messages and over-reading
- `avoidant`: direct emotional pressure makes them want to retreat
- `has trouble apologizing`: they repair through indirect gestures instead of saying "sorry"
- `soft-hearted under a tough exterior`: "whatever" often means they care a lot
- `sarcastic speaker`: understanding the subtext is essential
- `talkative`: a good mood means many messages; unusual silence means something is wrong
- `quiet type`: long messages matter a lot; silence does not automatically mean indifference
- `reopens old arguments`: old incidents remain stored and may come back during conflict
- `very jealous`: they say "it's fine" but keep asking for details
- `cuts contact completely`: after the breakup they may block, delete, or refuse to respond
- `initiated the breakup`: they said it first, but that does not always mean they wanted clean separation
- `acts aloof`: the surface looks calm, but sore spots can trigger sudden intensity
- `creates uncertainty`: they alternate between warmth and distance in a hard-to-read way

---

## Output Requirements

- Language: English
- For dimensions with insufficient evidence, mark them as `(insufficient message evidence; inferred from tags below)`
- For conclusions backed by actual messages, quote the original lines
- If manual tags conflict with message analysis, output both versions and label them clearly
- If total message count is below 200, put this warning at the top: `⚠️ Message sample is limited; persona confidence is lower`
