# Clarification cycle

Use this workflow after generating a diagram with open business questions.

## 1. Export questions

```text
python scripts/question_cycle.py export process.json --output process-questions.txt
```

Give the TXT file to the business reviewer. They must write below each
`RESPUESTA:` marker without changing `[[Q...]]` identifiers.

## 2. Parse answers

```text
python scripts/question_cycle.py parse process.json process-questions.txt --output process-answers.json
```

Read the source diagram and parsed answers together. Treat answers as new
business evidence, not as direct JSON patches.

## 3. Reconcile each answer

For every answered question:

1. Identify the affected nodes, edges, groups, labels, assumptions, or rules.
2. Check whether the answer is complete and consistent with the transcript and
   with other answers.
3. If complete, update the diagram, remove the question from `open_questions`,
   and append it to `resolved_questions` with `id`, `question`, `answer`, and a
   concise `resolution` describing the diagram change.
4. If incomplete, ambiguous, or contradictory, create a focused follow-up in
   `open_questions`. Use an ID such as `Q003-F1`, set `parent_id: "Q003"`, and
   reference the affected nodes in `related_nodes`.
5. Never remove a `?` node until its missing meaning is represented by a
   concrete node, edge, label, or rule.

## 4. Regenerate

Render the updated HTML and export a fresh TXT. Stop when there are no open
questions or the reviewer explicitly accepts the remaining unknowns.

Keep question IDs stable. Never reuse a resolved ID for a different question.
