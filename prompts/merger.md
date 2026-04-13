# Incremental Merge Prompt

## Task

The user added new chat records or screenshots. Merge the new content incrementally into the existing `persona.md` without overwriting established conclusions.

---

## Inputs

1. The existing `persona.md` (current version)
2. The new material (chat text and/or screenshot analysis output)

---

## Merge Rules

### Principles

- **Append incremental insight only**. Do not delete or modify existing content unless the new material directly contradicts it.
- **When a conflict appears**: new evidence overrides old inference; however, if the old content came from a user-authored rule such as the Correction layer, keep the old rule and explicitly mark the conflict.

### Processing Steps

1. Analyze the new material with `chat_analyzer.md` and extract any new behavior data
2. Compare old and new findings:
   - **Same conclusion**: skip it, do not duplicate
   - **New evidence**: append it to the relevant layer and label it with `(added: {date})`
   - **Direct contradiction**: annotate the original line with `⚠️ New record conflicts with this: {summary of new evidence}` for the user to judge
3. Update the message count and version number in `meta.json`

### Merge Targets by New Content Type

| New Content Type | Merge Target |
|------------------|--------------|
| New catchphrases / high-frequency words | Layer 2 expression style |
| New emoji usage | Layer 2 signature emoji |
| New conflict scenario | Layer 4 conflict chain |
| New reconciliation style | Layer 4 repair signals |
| New emotional-expression pattern | Layer 3 emotional behavior |
| Content that conflicts with an existing conclusion | Add a `⚠️` annotation instead of overwriting automatically |

---

## Output

Output the `persona.md` diff for the incremental section in this format:

```text
[Merge Report]
New messages: {N}
Updated layers: {list}
Conflicts found: {yes/no; list conflicts if any}

[Specific Changes]
{list the additions or annotations layer by layer}
```

Then output the updated full `persona.md`.
