#!/usr/bin/env python3
"""Export editable business questions and parse their answers deterministically."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

QUESTION_ID_RE = re.compile(r"^Q\d{3}(?:-F\d+)?$")
START_RE = re.compile(r"^\[\[(Q\d{3}(?:-F\d+)?)\]\]$")
END_RE = re.compile(r"^\[\[/((?:Q\d{3})(?:-F\d+)?)\]\]$")
ANSWER_MARKER = "RESPUESTA:"


def normalized_questions(diagram: dict) -> list[dict]:
    result = []
    seen = set()
    node_ids = {node.get("id") for node in diagram.get("nodes", []) if isinstance(node, dict)}
    for index, item in enumerate(diagram.get("open_questions", []), 1):
        if isinstance(item, str):
            question = {"id": f"Q{index:03d}", "question": item, "related_nodes": []}
        elif isinstance(item, dict):
            question = {
                "id": item.get("id", ""),
                "question": item.get("question", ""),
                "related_nodes": item.get("related_nodes", []),
                "parent_id": item.get("parent_id"),
            }
        else:
            raise ValueError(f"invalid question at position {index}")
        qid = question["id"]
        if not QUESTION_ID_RE.fullmatch(qid) or qid in seen:
            raise ValueError(f"invalid or duplicate question id: {qid!r}")
        if not isinstance(question["question"], str) or not question["question"].strip():
            raise ValueError(f"{qid} must have a non-empty question")
        if not isinstance(question["related_nodes"], list):
            raise ValueError(f"{qid}.related_nodes must be an array")
        unknown_nodes = set(question["related_nodes"]) - node_ids
        if unknown_nodes:
            raise ValueError(f"{qid} references unknown nodes: {', '.join(sorted(unknown_nodes))}")
        seen.add(qid)
        result.append(question)
    return result


def export_questions(diagram: dict) -> str:
    questions = normalized_questions(diagram)
    lines = [
        f"PREGUNTAS DE NEGOCIO — {diagram.get('title', 'Diagrama')}",
        "",
        "INSTRUCCIONES",
        "- Escriba cada respuesta debajo de RESPUESTA:.",
        "- Puede usar varias líneas.",
        "- Si no conoce una respuesta, escriba: NO SÉ.",
        "- No cambie los identificadores [[Q...]].",
        "",
    ]
    if not questions:
        return "\n".join(lines + ["No hay preguntas abiertas.", ""])
    for question in questions:
        lines.extend([
            f"[[{question['id']}]]",
            f"PREGUNTA: {question['question']}",
            ANSWER_MARKER,
            "",
            f"[[/{question['id']}]]",
            "",
        ])
    return "\n".join(lines)


def parse_answers(diagram: dict, text: str) -> dict:
    questions = {q["id"]: q for q in normalized_questions(diagram)}
    answers: dict[str, str] = {}
    current_id = None
    collecting = False
    buffer: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        start = START_RE.fullmatch(line.strip())
        end = END_RE.fullmatch(line.strip())
        if start:
            if current_id is not None:
                raise ValueError(f"nested question block near {start.group(1)}")
            current_id = start.group(1)
            if current_id not in questions:
                raise ValueError(f"unknown question id in answers file: {current_id}")
            collecting = False
            buffer = []
        elif end:
            if current_id != end.group(1):
                raise ValueError(f"mismatched closing marker for {end.group(1)}")
            answers[current_id] = "\n".join(buffer).strip()
            current_id = None
            collecting = False
            buffer = []
        elif current_id and line.strip() == ANSWER_MARKER:
            collecting = True
        elif current_id and collecting:
            buffer.append(line)
    if current_id is not None:
        raise ValueError(f"unclosed question block: {current_id}")
    missing = set(questions) - set(answers)
    if missing:
        raise ValueError(f"missing question blocks: {', '.join(sorted(missing))}")
    records = []
    for qid, question in questions.items():
        answer = answers[qid]
        records.append({
            **question,
            "answer": answer,
            "answered": bool(answer) and answer.strip().upper() not in {"NO SÉ", "NO SE", "DESCONOCIDO"},
        })
    return {
        "diagram_title": diagram.get("title", ""),
        "questions": records,
        "answered_count": sum(1 for record in records if record["answered"]),
        "open_count": sum(1 for record in records if not record["answered"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export", help="Create an editable TXT questionnaire")
    export.add_argument("diagram", type=Path)
    export.add_argument("--output", "-o", type=Path, required=True)
    parse = sub.add_parser("parse", help="Convert edited answers to structured JSON")
    parse.add_argument("diagram", type=Path)
    parse.add_argument("answers", type=Path)
    parse.add_argument("--output", "-o", type=Path, required=True)
    args = parser.parse_args()
    diagram = json.loads(args.diagram.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.command == "export":
        args.output.write_text(export_questions(diagram), encoding="utf-8")
        print(f"Exported {len(normalized_questions(diagram))} questions to {args.output}")
    else:
        result = parse_answers(diagram, args.answers.read_text(encoding="utf-8"))
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Parsed {len(result['questions'])} questions: {result['answered_count']} answered, {result['open_count']} open")


if __name__ == "__main__":
    main()
