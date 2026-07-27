#!/usr/bin/env python3
"""Render a transcript-derived diagram JSON as a self-contained HTML/SVG artifact."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

KINDS = {"start", "end", "process", "decision", "database", "file", "api", "person", "queue", "report", "generic"}
ID_RE = re.compile(r"^[a-z0-9_-]+$")

ICONS = {
    "start": '<circle cx="12" cy="12" r="7"/><path d="m10 8 6 4-6 4z"/>',
    "end": '<circle cx="12" cy="12" r="8"/><rect x="9" y="9" width="6" height="6" rx="1"/>',
    "process": '<rect x="4" y="5" width="16" height="14" rx="3"/><path d="M8 9h8M8 13h6"/>',
    "transform": '<path d="M4 6h9l-2-2m2 2-2 2M20 18h-9l2 2m-2-2 2-2"/><path d="M6 10v6m12-8v6"/>',
    "decision": '<path d="m12 3 9 9-9 9-9-9z"/><path d="M9 12h6"/>',
    "database": '<ellipse cx="12" cy="5.5" rx="8" ry="3.5"/><path d="M4 5.5v6c0 2 3.6 3.5 8 3.5s8-1.5 8-3.5v-6M4 11.5v6c0 2 3.6 3.5 8 3.5s8-1.5 8-3.5v-6"/>',
    "excel": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M9 3v18M13 8h7M13 13h7M13 18h7M6 9l2 5m0-5-2 5"/>',
    "file": '<path d="M6 2h8l4 4v16H6z"/><path d="M14 2v5h5M9 12h6M9 16h6"/>',
    "api": '<path d="M8 7H5a3 3 0 0 0 0 6h3m8-6h3a3 3 0 0 1 0 6h-3M8 10h8M8 14h8"/>',
    "cloud": '<path d="M7 18h11a4 4 0 0 0 .4-8A7 7 0 0 0 5 9a4.5 4.5 0 0 0 2 9z"/>',
    "queue": '<circle cx="6" cy="7" r="2"/><circle cx="6" cy="17" r="2"/><path d="M10 7h10M10 17h10M13 12h7"/>',
    "person": '<circle cx="12" cy="7" r="4"/><path d="M4 21c.7-5 3.3-8 8-8s7.3 3 8 8"/>',
    "report": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7 16v-4m5 4V8m5 8v-6"/>',
    "email": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/>',
    "question": '<circle cx="12" cy="12" r="9"/><path d="M9.7 9a2.5 2.5 0 1 1 3.7 2.2c-.9.5-1.4 1-1.4 2.1M12 17h.01"/>',
    "generic": '<rect x="4" y="4" width="16" height="16" rx="4"/><path d="M8 12h8M12 8v8"/>',
}


def validate(data: dict) -> None:
    if not isinstance(data.get("title"), str) or not data["title"].strip():
        raise ValueError("title must be a non-empty string")
    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("nodes and edges must be arrays")
    ids = set()
    for node in nodes:
        node_id = node.get("id", "")
        if not ID_RE.fullmatch(node_id) or node_id in ids:
            raise ValueError(f"invalid or duplicate node id: {node_id!r}")
        ids.add(node_id)
        if node.get("kind", "generic") not in KINDS:
            raise ValueError(f"invalid kind for {node_id}")
        for axis in ("stage", "lane"):
            if not isinstance(node.get(axis), int) or node[axis] < 0:
                raise ValueError(f"{node_id}.{axis} must be a non-negative integer")
    for edge in edges:
        if edge.get("from") not in ids or edge.get("to") not in ids:
            raise ValueError(f"edge references an unknown node: {edge}")


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def render(data: dict) -> str:
    groups = {g["id"]: g for g in data.get("groups", [])}
    max_stage = max((n["stage"] for n in data["nodes"]), default=0)
    max_lane = max((n["lane"] for n in data["nodes"]), default=0)
    width = max(1100, 260 + (max_stage + 1) * 270)
    height = max(620, 250 + (max_lane + 1) * 190)
    # A4 landscape at 96 CSS px/in is about 1123x794 px. Reserve space for
    # margins and the title, then fit the complete canvas onto one print page.
    print_scale = min(1.0, 1020 / width, 560 / height)
    print_width = round(width * print_scale, 2)
    print_height = round(height * print_scale, 2)
    node_html = []
    for n in data["nodes"]:
        color = groups.get(n.get("group"), {}).get("color", "#475569")
        icon = ICONS.get(n.get("icon"), ICONS.get(n.get("kind"), ICONS["generic"]))
        left, top = 120 + n["stage"] * 270, 175 + n["lane"] * 190
        node_html.append(
            f'<article class="node kind-{esc(n.get("kind", "generic"))}" id="node-{esc(n["id"])}" '
            f'data-id="{esc(n["id"])}" style="--accent:{esc(color)};left:{left}px;top:{top}px">'
            f'<span class="icon"><svg viewBox="0 0 24 24">{icon}</svg></span>'
            f'<span class="copy"><strong>{esc(n.get("title"))}</strong>'
            f'<small>{esc(n.get("detail"))}</small></span></article>'
        )
    group_chips = "".join(
        f'<span><i style="background:{esc(g.get("color", "#475569"))}"></i>{esc(g.get("label", g["id"]))}</span>'
        for g in data.get("groups", [])
    )
    notes = []
    if data.get("assumptions"):
        notes.append("<section><h3>Supuestos</h3><ul>" + "".join(f"<li>{esc(x)}</li>" for x in data["assumptions"]) + "</ul></section>")
    if data.get("open_questions"):
        notes.append("<section><h3>Preguntas abiertas</h3><ul>" + "".join(f"<li>{esc(x)}</li>" for x in data["open_questions"]) + "</ul></section>")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    template = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;color:#172033;background:#eef2f7;--print-scale:__PRINT_SCALE__;--print-width:__PRINT_WIDTH__px;--print-height:__PRINT_HEIGHT__px}
*{box-sizing:border-box}body{margin:0}.toolbar{position:sticky;top:0;z-index:20;display:flex;gap:10px;justify-content:flex-end;padding:12px 22px;background:#0f172acc;backdrop-filter:blur(12px)}
button{border:1px solid #ffffff38;border-radius:10px;padding:9px 14px;color:white;background:#334155;cursor:pointer;font-weight:700}button.primary{background:#2563eb}
.page{width:min(96vw,calc(__WIDTH__px + 2px));margin:28px auto;background:#fff;border:1px solid #dbe3ef;border-radius:22px;box-shadow:0 20px 55px #26364d22;overflow:hidden}
header{padding:30px 38px 22px;background:linear-gradient(135deg,#f8fbff,#eef5ff);border-bottom:1px solid #e3eaf4}h1{font-size:28px;letter-spacing:-.035em;margin:0 0 7px}header p{margin:0;color:#64748b}.legend{display:flex;gap:17px;flex-wrap:wrap;margin-top:18px;color:#475569;font-size:12px;font-weight:700}.legend span{display:flex;align-items:center;gap:7px}.legend i{width:9px;height:9px;border-radius:99px}
.canvas-wrap{width:100%;overflow-x:auto;overflow-y:hidden;scrollbar-gutter:stable;background:#fff}
.canvas{position:relative;width:__WIDTH__px;height:__HEIGHT__px;background-image:radial-gradient(#cbd5e1 1px,transparent 1px);background-size:22px 22px;transform-origin:top left}
#edges{position:absolute;inset:0;width:100%;height:100%;overflow:visible}.node{position:absolute;width:205px;min-height:82px;display:flex;align-items:center;gap:13px;padding:15px;background:#fff;border:1px solid #dce4ef;border-top:4px solid var(--accent);border-radius:15px;box-shadow:0 9px 24px #21304a19}
.node .icon{width:45px;height:45px;flex:0 0 45px;display:grid;place-items:center;border-radius:12px;color:var(--accent);background:color-mix(in srgb,var(--accent) 11%,white)}.icon svg{width:25px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.copy{min-width:0}.copy strong{display:block;font-size:14px;line-height:1.25}.copy small{display:block;margin-top:5px;color:#64748b;font-size:11px;line-height:1.3}.copy small:empty{display:none}.kind-decision{border-radius:5px}
.notes{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;padding:0 30px 28px}.notes section{background:#f8fafc;border:1px solid #e2e8f0;border-radius:13px;padding:15px 18px}.notes h3{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#475569;margin:0 0 9px}.notes ul{margin:0;padding-left:18px;font-size:12px;color:#475569}.edge-label{font-size:11px;font-weight:700;fill:#475569;paint-order:stroke;stroke:#fff;stroke-width:5px;stroke-linejoin:round}
@media(max-width:900px){.toolbar{position:static}.page{width:100vw;margin:0;border-radius:0}.canvas-wrap{scrollbar-gutter:auto}}
@media print{
  @page{size:A4 landscape;margin:8mm}
  html,body{width:100%;background:white}
  .toolbar{display:none}
  .page{width:100%;margin:0;border:0;border-radius:0;box-shadow:none;overflow:visible}
  header{padding:12px 18px 10px;background:white}h1{font-size:20px}.legend{margin-top:8px}
  .canvas-wrap{width:var(--print-width);height:var(--print-height);margin:0 auto;overflow:visible;break-inside:avoid}
  .canvas{transform:scale(var(--print-scale))}
  .notes{padding:12px 18px 0;break-inside:auto}
}
</style></head><body><nav class="toolbar"><button onclick="downloadSVG()">Descargar SVG</button><button class="primary" onclick="printDiagram()">PDF / Imprimir · Horizontal</button></nav>
<main class="page"><header><h1>__TITLE__</h1><p>__SUBTITLE__</p><div class="legend">__LEGEND__</div></header>
<div class="canvas-wrap" id="canvas-wrap"><div class="canvas" id="canvas"><svg id="edges"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#64748b"/></marker></defs></svg>__NODES__</div></div>
<aside class="notes">__NOTES__</aside></main><script>
const model=__PAYLOAD__;
function draw(){const svg=document.querySelector("#edges"),canvas=document.querySelector("#canvas"),box=canvas.getBoundingClientRect();svg.querySelectorAll(".edge").forEach(x=>x.remove());
for(const e of model.edges){const a=document.querySelector(`[data-id="${CSS.escape(e.from)}"]`),b=document.querySelector(`[data-id="${CSS.escape(e.to)}"]`);if(!a||!b)continue;
const ar=a.getBoundingClientRect(),br=b.getBoundingClientRect(),x1=ar.right-box.left,y1=ar.top+ar.height/2-box.top,x2=br.left-box.left,y2=br.top+br.height/2-box.top,mx=(x1+x2)/2;
const g=document.createElementNS("http://www.w3.org/2000/svg","g");g.classList.add("edge");const p=document.createElementNS(g.namespaceURI,"path");p.setAttribute("d",`M${x1} ${y1} C${mx} ${y1},${mx} ${y2},${x2} ${y2}`);p.setAttribute("fill","none");p.setAttribute("stroke","#64748b");p.setAttribute("stroke-width","2");p.setAttribute("marker-end","url(#arrow)");if(e.style==="dashed")p.setAttribute("stroke-dasharray","6 5");g.appendChild(p);
if(e.label){const t=document.createElementNS(g.namespaceURI,"text");t.setAttribute("x",mx);t.setAttribute("y",(y1+y2)/2-7);t.setAttribute("text-anchor","middle");t.setAttribute("class","edge-label");t.textContent=e.label;g.appendChild(t)}svg.appendChild(g)}}
function downloadSVG(){draw();const c=document.querySelector("#canvas").cloneNode(true),s=c.querySelector("svg");const css=`.node{font-family:Arial,sans-serif;width:205px;min-height:82px;display:flex;align-items:center;gap:13px;padding:15px;background:#fff;border:1px solid #dce4ef;border-top:4px solid var(--accent);border-radius:15px;box-sizing:border-box}.icon{width:45px;height:45px;flex:0 0 45px;display:grid;place-items:center;border-radius:12px;color:var(--accent);background:#f1f5f9}.icon svg{width:25px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.copy strong{display:block;font-size:14px;color:#172033}.copy small{display:block;margin-top:5px;color:#64748b;font-size:11px}`;const defs=s.querySelector("defs"),style=document.createElementNS(s.namespaceURI,"style");style.textContent=css;defs.appendChild(style);c.querySelectorAll(".node").forEach(n=>{const x=parseFloat(n.style.left),y=parseFloat(n.style.top),fo=document.createElementNS("http://www.w3.org/2000/svg","foreignObject");fo.setAttribute("x",x);fo.setAttribute("y",y);fo.setAttribute("width",205);fo.setAttribute("height",105);fo.innerHTML=`<div xmlns="http://www.w3.org/1999/xhtml">${n.outerHTML.replace(/position:absolute/,"position:relative").replace(/left:[^;]+;/,"left:0;").replace(/top:[^;]+;/,"top:0;")}</div>`;s.appendChild(fo);n.remove()});s.setAttribute("xmlns","http://www.w3.org/2000/svg");s.setAttribute("width","__WIDTH__");s.setAttribute("height","__HEIGHT__");const blob=new Blob([new XMLSerializer().serializeToString(s)],{type:"image/svg+xml"}),a=document.createElement("a"),url=URL.createObjectURL(blob);a.href=url;a.download="diagrama.svg";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
function printDiagram(){draw();window.print()}
addEventListener("load",draw);addEventListener("resize",draw);
</script></body></html>"""
    replacements = {
        "__TITLE__": esc(data["title"]), "__SUBTITLE__": esc(data.get("subtitle", "")),
        "__WIDTH__": str(width), "__HEIGHT__": str(height), "__LEGEND__": group_chips,
        "__PRINT_SCALE__": f"{print_scale:.6f}", "__PRINT_WIDTH__": str(print_width),
        "__PRINT_HEIGHT__": str(print_height),
        "__NODES__": "".join(node_html), "__NOTES__": "".join(notes), "__PAYLOAD__": payload,
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Diagram JSON")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Output HTML")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    validate(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data), encoding="utf-8")
    print(f"Rendered {len(data['nodes'])} nodes to {args.output}")


if __name__ == "__main__":
    main()
