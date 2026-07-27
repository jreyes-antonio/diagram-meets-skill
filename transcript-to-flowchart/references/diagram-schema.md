# Diagram JSON schema

Use UTF-8 JSON with this shape:

```json
{
  "title": "Flujo de carga de ventas",
  "subtitle": "Estado actual · Fuente: reunión 2026-07-27",
  "groups": [
    {"id": "source", "label": "Origen", "color": "#7c3aed"},
    {"id": "platform", "label": "Plataforma de datos", "color": "#2563eb"}
  ],
  "nodes": [
    {
      "id": "excel",
      "title": "Archivo de ventas",
      "detail": "Carga manual diaria",
      "kind": "file",
      "icon": "excel",
      "stage": 0,
      "lane": 0,
      "group": "source"
    }
  ],
  "edges": [
    {"from": "excel", "to": "validate", "label": "Cada mañana", "style": "solid"}
  ],
  "assumptions": ["La carga ocurre una vez al día."],
  "open_questions": [
    {
      "id": "Q001",
      "question": "¿Quién corrige los registros rechazados?",
      "related_nodes": ["validate"]
    }
  ],
  "resolved_questions": []
}
```

Required top-level fields: `title`, `nodes`, and `edges`.

Node fields:

- `id`: unique lowercase identifier using letters, numbers, `_`, or `-`.
- `title`: short visible label.
- `detail`: optional secondary line.
- `kind`: `start`, `end`, `process`, `decision`, `database`, `file`, `api`, `person`, `queue`, `report`, or `generic`.
- `icon`: key from the icon catalog.
- `stage`: non-negative integer; controls left-to-right position.
- `lane`: non-negative integer; controls top-to-bottom position.
- `group`: optional group ID.

Edge fields:

- `from`, `to`: existing node IDs.
- `label`: optional concise label.
- `style`: optional `solid` or `dashed`; use dashed for optional or inferred paths.

Colors must be six-digit hexadecimal values. Avoid embedding HTML in any string.

For missing information, create a `generic` node with `icon: question`, connect it
with a dashed edge, and repeat the clarification needed in `open_questions`.

Question fields:

- `id`: stable `Q001`-style identifier. Follow-ups use `Q001-F1`.
- `question`: one focused business question.
- `related_nodes`: IDs of nodes affected by the answer.
- `parent_id`: optional original question ID for a follow-up.

For backward compatibility, `open_questions` may contain strings. Convert them
to structured objects before the first answer-reconciliation cycle.

Resolved question fields:

- `id`, `question`, `answer`: preserve the reviewed evidence.
- `resolution`: concise description of what changed in the diagram.
