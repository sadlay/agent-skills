# Improve Skill Prompt

Use this prompt after a real usage failure or friction point.

```text
Improve the skill at `<skill-path>` based on the usage trace below.

Usage trace:
- User request: <paste request>
- What the agent did: <paste summary or transcript>
- What went wrong: <paste observation>
- Desired behavior: <paste expectation>

Instructions:
1. Decide whether the issue is triggering, workflow, reference material, script behavior, safety, or platform compatibility.
2. Make the smallest change that fixes the observed issue without overfitting to one prompt.
3. If the skill is becoming too long, move details into a directly linked file in `references/`.
4. If a script changes, run a representative command.
5. Add an eval prompt under `evals/<skill-name>/prompts.md` when the failure is likely to recur.
6. Run `python3 scripts/validate-skills`.

Return:
- Files changed.
- Why the change fixes the observed issue.
- Verification performed.
```
