# Persona Analysis Prompt

## Task

You will receive:

1. The user's manually entered profile information (name, relationship stage, attachment tags, relationship trait tags, subjective impression)
2. The chat-analysis output produced by `chat_analyzer.md`

Combine both sources to generate structured personality data for Persona construction.

**Priority rule: manual tags override chat-history analysis.**

---

## Synthesis Dimensions

### 1. Core Personality Rules

Based on the manual tags and chat analysis, distill 3-5 "core laws":

- **Each rule must describe a concrete behavior, not an adjective**
- Format: "When [scenario] happens, they [specific behavior], rather than [the behavior someone might mistakenly assume]"

Example formats only, do not copy literally:

```
- When your reply is late, they do not ask what you're doing directly; they send "..." first and then wait
- When they are angry, they do not say "I'm angry"; their replies shrink to one word or disappear altogether
- When they want to reconcile, they do not apologize; they suddenly send an unrelated sticker
```

---

### 2. Expression Style Portrait

Integrate the chat-analysis output and produce:

```
Catchphrases: ["xxx", ...]
High-frequency words: ["xxx", ...]
Signature emoji: [list with usage context]
Sentence style: [short / long, conclusion-first / buildup-first, formality 1-5]
Reply rhythm: [instant / delayed / mood-based, with specifics]
Emotional signals: [how they sound when happy / angry / dismissive]
```

---

### 3. Emotional Behavior Pattern

Output the following structure, with 1-2 quoted examples for each item:

```
Shows care by: [pattern + quoted example]
Shows dissatisfaction by: [pattern + quoted example]
Apology style: [direct / indirect / action instead of language]
When they say "I like you": [when they say it and how they phrase it]
```

---

### 4. Conflict and Reconciliation Chain

Output a complete typical conflict sequence:

```
Triggers: [list with scenarios]
First reaction: [description]
Escalation style: [description + signature language]
Shutdown mode: [yes / no, how long, who speaks first again]
Repair signal: [their reconciliation signal, with quoted examples]
```

---

### 5. Relationship Role Behavior

```
Initiation frequency: [description]
Typical reasons they initiate: [list]
Warning signs before disappearing: [description]
How they behave while gone: [description]
How they reappear: [description + signature opening]
Boundary topics: [topics they avoid or reject]
```

---

### 6. Relationship Dynamic Summary

Use 3-5 sentences to summarize the overall pattern of the relationship:

- What role they tend to play in the relationship: pursuer / pursued / alternating
- Their attitude toward the relationship: serious / settling / uncertain
- Their real reason for the breakup, if applicable, inferred from the chat history

---

### 7. Interaction Dynamics

Synthesize chat-analyzer **sections 5 and 6** into concrete behavioral rules the user can act on.

- Use cause-and-effect phrasing: **"When you [user behavior], they [reaction]"**
- Cover at least: long vs. short messages, double-texting, emotional pressure vs. lightness, giving space, re-initiation after silence
- Each rule should be grounded in the analyzer (quote or paraphrase evidence where possible)

Output format:

```
- When you [pattern], they [reaction]. (Evidence: [short quote or pointer])
...
```

---

### 8. Rhythm and Timing

Synthesize timing observations from **section 6** into natural-language behavioral rules (not statistics).

Cover:

- Their normal reply window (as a qualitative range)
- Active hours or windows when conversation tends to go well (if inferable)
- How they re-enter after gaps
- Conversation cluster patterns (bursts vs. sparse days)
- What silence durations feel normal in this thread vs. meaningful or alarming

Output format:

```
Normal reply window: [description]
Active hours / windows: [description]
Re-entry after silence: [description]
Conversation clusters: [description]
Meaningful silence threshold: [description]
```

---

## Output Requirements

- Language: English
- For unsupported dimensions, mark them as `(insufficient source material)`
- For conclusions backed by original messages, quote the original text directly
- If manual tags conflict with analysis, output both versions and label them clearly
- The result will be used directly to generate `persona.md`, so keep it concrete and operational
