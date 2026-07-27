---
name: transcript-to-flowchart
description: Convert meeting transcripts, process descriptions, workshop notes, or requirements into polished flowcharts and architecture diagrams. Use when an agent must extract actors, systems, decisions, data stores, transformations, handoffs, parallel paths, and uncertainties from free-form text, then deliver a portable HTML diagram that can be downloaded as SVG or printed to PDF.
---

# Transcript to Flowchart

Convert unstructured conversation into an auditable process model, then render it with the bundled deterministic renderer.

## Workflow

1. Read the complete transcript before modeling.
2. Separate explicit facts from inferred relationships. Never silently invent a step.
3. Identify:
   - process boundary, start, and outcome;
   - actors or teams;
   - systems, files, databases, APIs, and reports;
   - transformations and validations;
   - decisions, alternatives, retries, and parallel branches;
   - labels stated for connections, such as batch, streaming, manual, or scheduled;
   - unresolved questions or contradictions.
4. Create a JSON file that conforms to `references/diagram-schema.md`.
5. Prefer 5–12 nodes per view. Split a dense process into a high-level overview and detailed subflows.
6. Select icons using `references/icon-catalog.md`. Use `generic` rather than guessing a vendor product.
   Represent missing sources, rules, owners, transformations, or destinations as `kind: generic`, `icon: question`, with a dashed edge. Repeat each clarification in `open_questions`.
7. Render with:

   ```text
   python scripts/render_diagram.py process.json --output process.html
   ```

8. Open the HTML and verify every label, edge, decision, and assumption against the transcript.
9. Deliver the JSON source and HTML. To create a PDF, open the HTML, click **PDF / Imprimir**, and choose **Guardar como PDF**. To create a vector image, click **Descargar SVG**.

## Modeling rules

- Preserve the language used by the requester unless asked to translate.
- Write concise node titles with optional detail; do not paste transcript paragraphs into nodes.
- Use `kind: decision` only for a real condition with labeled outgoing edges.
- Use `kind: database` for persistent structured storage and `kind: file` for spreadsheets, CSV, documents, or object files.
- Use `group` for phases, domains, platforms, or teams; do not use it merely for color.
- Use edge labels for transport, cadence, or condition. Prefer `Sí`/`No`, `Batch`, `Streaming`, `API`, or `Manual` over sentences.
- Record uncertain interpretations in `assumptions`; show them in the diagram's notes panel.
- Record omitted details in `open_questions`; do not bury them in a node.
- Do not reproduce confidential names in a sample or public repository unless authorized.

## Layout guidance

- Assign `stage` from left to right, starting at 0.
- Assign `lane` from top to bottom within a stage.
- Give parallel alternatives the same `stage` and distinct `lane` values.
- Keep the principal happy path near the vertical center.
- Avoid backward edges. If a loop is necessary, label it clearly.
- Use at most six groups and keep group names short.

## Validation checklist

- Every non-start node has an incoming edge unless intentionally independent.
- Every non-end node has an outgoing edge unless it is an external output.
- Every decision has at least two labeled outgoing edges.
- IDs are unique and every edge references existing IDs.
- No transcript assertion is promoted to fact when it was only a suggestion.
- The HTML works without internet access and remains readable when printed.

Read `references/diagram-schema.md` whenever creating JSON. Read `references/icon-catalog.md` when choosing or extending icons.
