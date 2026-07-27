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
  "open_questions": ["¿Quién corrige los registros rechazados?"]
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
