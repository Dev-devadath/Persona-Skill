# Correction Handling Prompt

## Task

The user corrected a behavior in the Persona through conversation. Write that correction into the Correction layer of `persona.md` and make it take effect immediately.

---

## Detect Correction Intent

The following expression patterns should trigger correction handling:

- "That's not right, they wouldn't do that."
- "In that situation, they would..."
- "No, when they're angry they..."
- "You got that wrong, they actually..."
- "Add one more rule: they would never..."

---

## Processing Steps

1. **Identify the scenario**: In what situation did this correction happen?
2. **Identify the incorrect behavior**: What is the current Persona getting wrong?
3. **Record the correct behavior**: What behavior did the user describe instead?
4. **Write it in this format**:

```markdown
## Correction Log

- [Scenario: {scenario description}] Wrong: {incorrect behavior}; Correct: {correct behavior}
  Source: user correction, {date}
```

5. **Check whether Layer 0 should also be updated**: If this correction reflects a core behavior rule, consider syncing it into Layer 0 as well.

---

## Example

User says: "That's not right. When they're angry they wouldn't say 'I don't want to talk anymore.' They would just stop replying and disappear for a whole day."

→ Correction entry:

```markdown
- [Scenario: reaction when angry] Wrong: ending the conversation by saying "I don't want to talk anymore"; Correct: stop replying immediately and potentially disappear for a whole day
  Source: user correction, 2026-03-31
```

→ Also check Layer 4's conflict / shutdown pattern and update it if there is a conflict.

---

## Correction Capacity

- Keep at most 50 entries
- Once the limit is exceeded, merge similar situations into a more general rule, write that rule into the appropriate layer, and remove the older correction entries
