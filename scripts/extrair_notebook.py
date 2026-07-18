#!/usr/bin/env python3
"""Extrai um notebook do NotebookLM para um vault Obsidian minimalista."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validar_nota.py"
PROMPT = """Create a comprehensive briefing document that synthesizes the main themes and ideas from the sources. Start with a concise Executive Summary that presents the most critical takeaways upfront. The body of the document must provide a detailed and thorough examination of the main themes, evidence, and conclusions found in the sources. This analysis should be structured logically with headings and bullet points to ensure clarity. The tone must be objective and incisive.

Escreva em português do Brasil. A primeira seção deve ser exatamente ## 1. Sumário Executivo; continue com seções H2 numeradas."""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-") or "notebook"


def now() -> str:
    return datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec="seconds")


def frontmatter(data: dict[str, Any]) -> str:
    return "---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False).strip() + "\n---\n"


def cli(args: list[str]) -> bytes:
    result = subprocess.run([sys.executable, "-m", "notebooklm", *args], capture_output=True)
    if result.returncode:
        message = result.stderr.decode("utf-8", "replace").strip()
        detail = result.stdout.decode("utf-8", "replace").strip()
        raise RuntimeError(message or detail or f"falha: {' '.join(args)}")
    return result.stdout


def request(args: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(cli([*args, "--json"]).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"{label} não retornou JSON UTF-8 válido: {error}") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} não retornou objeto JSON")
    return value


def find_id(value: Any) -> str | None:
    if isinstance(value, dict):
        for key in ("artifact_id", "task_id", "note_id", "id"):
            if isinstance(value.get(key), str) and value[key].strip():
                return value[key]
        for child in value.values():
            found = find_id(child)
            if found:
                return found
    if isinstance(value, list):
        for child in value:
            found = find_id(child)
            if found:
                return found
    return None


def wait(notebook: str, artifact: str) -> None:
    value = request(["artifact", "wait", artifact, "-n", notebook, "--timeout", "600"], "artefato")
    status = str(value.get("status") or value.get("artifact", {}).get("status") or "completed").lower()
    if status not in {"completed", "complete", "ready"}:
        raise RuntimeError(f"artefato {artifact} terminou com status {status}")


def sources(notebook: str) -> tuple[str, list[dict[str, Any]]]:
    value = request(["source", "list", "-n", notebook], "inventário")
    entries = value.get("sources") or value.get("items") or []
    if not isinstance(entries, list):
        raise RuntimeError("inventário sem lista de fontes")
    result = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        source_id = str(item.get("id") or item.get("source_id") or "").strip()
        title = str(item.get("title") or item.get("name") or source_id).strip()
        if not source_id or not title:
            raise RuntimeError("fonte sem ID ou título")
        url = item.get("url") or item.get("source_url")
        source_type = str(item.get("type") or item.get("source_type") or "unknown").lower()
        source_type = source_type.removeprefix("sourcetype.")
        result.append(
            {
                "title": title,
                "url": str(url).strip() if url else None,
                "type": source_type,
                "notebooklm_source_id": source_id,
            }
        )
    title = str(value.get("notebook_title") or value.get("title") or "Notebook sem título")
    return title, result


def get_report(notebook: str, output: Path) -> str:
    value = request(
        ["generate", "report", PROMPT, "--format", "custom", "--language", "pt_BR", "-n", notebook],
        "briefing",
    )
    artifact = find_id(value)
    if not artifact:
        raise RuntimeError("briefing sem ID do artefato")
    wait(notebook, artifact)
    cli(["download", "report", str(output), "--artifact", artifact, "-n", notebook, "--force"])
    text = output.read_text(encoding="utf-8-sig")
    if not text.strip() or "Ã" in text or "�" in text:
        raise RuntimeError("briefing baixado não está em UTF-8 íntegro")
    return artifact


def as_node(value: Any) -> tuple[str, list[Any]] | None:
    if isinstance(value, str) and value.strip():
        return value.strip(), []
    if not isinstance(value, dict):
        return None
    label = next(
        (value[key] for key in ("label", "title", "name", "text", "content") if isinstance(value.get(key), str) and value[key].strip()),
        None,
    )
    children = next((value[key] for key in ("children", "nodes", "items", "branches") if isinstance(value.get(key), list)), [])
    return (str(label).strip(), children) if label else None


def root(value: Any) -> tuple[str, list[Any]]:
    item = as_node(value)
    if item:
        return item
    if isinstance(value, dict):
        for key in ("mind_map", "mindmap", "data", "result", "root"):
            if key in value:
                try:
                    return root(value[key])
                except RuntimeError:
                    pass
    raise RuntimeError("mapa mental não retornou árvore utilizável")


def mindmap_mermaid(value: dict[str, Any]) -> str:
    title, children = root(value)
    safe = lambda text: " ".join(text.replace("\n", " ").replace('"', "'").split())
    lines = ["mindmap", f"  root(({safe(title)}))"]

    def visit(nodes: list[Any], depth: int) -> None:
        for raw in nodes:
            item = as_node(raw)
            if not item:
                continue
            label, nested = item
            lines.append("  " * depth + safe(label))
            visit(nested, depth + 1)

    visit(children, 2)
    if len(lines) == 2:
        raise RuntimeError("mapa mental sem ramificações")
    tick = chr(96) * 3
    return tick + "mermaid\n" + "\n".join(lines) + "\n" + tick


def get_mindmap(notebook: str, output: Path) -> tuple[str, str]:
    value = request(["generate", "mind-map", "-n", notebook], "mapa mental")
    artifact = find_id(value)
    if not artifact:
        raise RuntimeError("mapa mental sem ID do artefato")
    wait(notebook, artifact)
    cli(["download", "mind-map", str(output), "--artifact", artifact, "-n", notebook, "--force"])
    try:
        payload = json.loads(output.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"mapa mental baixado não contém JSON UTF-8 válido: {error}") from error
    if not isinstance(payload, dict):
        raise RuntimeError("mapa mental baixado não contém objeto JSON")
    return artifact, mindmap_mermaid(payload)


def insert_mindmap(briefing: str, diagram: str) -> str:
    body = re.sub(r"\A---\n.*?\n---\s*\n", "", briefing, flags=re.DOTALL)
    body = re.sub(r"\A# .+?\n+", "", body).strip()
    body = re.sub(r"\n*## Mapa mental\n.*?(?=\n## |\Z)", "\n", body, flags=re.DOTALL)
    executive = re.search(r"^## 1\. Sumário Executivo\s*$", body, re.MULTILINE)
    if not executive:
        raise RuntimeError("briefing sem ## 1. Sumário Executivo")
    following = re.search(r"^## ", body[executive.end() :], re.MULTILINE)
    if not following:
        raise RuntimeError("briefing sem seção após Sumário Executivo")
    position = executive.end() + following.start()
    return body[:position].rstrip() + "\n\n## Mapa mental\n\n" + diagram + "\n\n" + body[position:].lstrip()


def display(link: str) -> str:
    return Path(link).stem.replace("-", " ")


def render(stage: Path, title: str, slug: str, briefing: str, data: dict[str, Any]) -> None:
    (stage / "neurons").mkdir(parents=True, exist_ok=True)
    folder = stage / "notebooks" / slug
    neurons = data["neuron_links"]
    related = data["related_summaries"]
    body = f"# {title}\n\n{briefing}\n\n## Neurônios conectáveis\n\n"
    body += "\n".join(f"- [{display(link)}]({link})" for link in neurons) if neurons else "- Nenhum neurônio canônico associado nesta extração."
    body += "\n\n## Resumos relacionados\n\n" + (
        "\n".join(f"- [{display(link)}]({link})" for link in related) if related else "- Nenhum resumo relacionado identificado."
    )
    body += "\n\n## Fontes originais\n\n"
    for source in data["source_links"]:
        if source["url"]:
            body += f"- [{source['title']}]({source['url']}) · {source['type']}\n"
        else:
            body += f"- {source['title']} · {source['type']} · URL não preservada pelo NotebookLM · ID {source['notebooklm_source_id']}\n"
    write(folder / f"{slug}.md", frontmatter(data) + "\n" + body)
    write(folder / "index.md", f"# {title}\n\n- [Resumo](/{(folder / f'{slug}.md').relative_to(stage).as_posix()})\n" + "".join(f"- [{display(link)}]({link})\n" for link in neurons))
    write(folder / "log.md", f"# Histórico\n\n## {data['timestamp'][:10]}\n\n- Criação ou atualização editorial com briefing e mapa mental nativos do NotebookLM.\n")


def publish(stage: Path, vault: Path, slug: str) -> None:
    target = vault / "notebooks" / slug
    source = stage / "notebooks" / slug
    target.parent.mkdir(parents=True, exist_ok=True)
    (vault / "neurons").mkdir(parents=True, exist_ok=True)
    backup = target.with_name("." + slug + ".backup")
    if backup.exists():
        shutil.rmtree(backup)
    if target.exists():
        target.rename(backup)
    try:
        shutil.copytree(source, target)
    except Exception:
        if backup.exists() and not target.exists():
            backup.rename(target)
        raise
    shutil.rmtree(backup, ignore_errors=True)
    graph = vault / ".obsidian" / "graph.json"
    config = json.loads(graph.read_text(encoding="utf-8")) if graph.exists() else {}
    config.update({"search": "-file:index -file:log", "showOrphans": False, "showTags": True})
    write(graph, json.dumps(config, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--notebook", required=True)
    parser.add_argument("--deck", required=True, type=Path)
    parser.add_argument("--description")
    parser.add_argument("--tag", action="append")
    parser.add_argument("--knowledge-domain", action="append")
    parser.add_argument("--neuron", action="append")
    parser.add_argument("--related-summary", action="append")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    title, source_links = sources(args.notebook)
    slug = slugify(title)
    with tempfile.TemporaryDirectory(prefix="notebooklm-") as temp:
        temp_path = Path(temp)
        stage = temp_path / "vault"
        briefing_id = get_report(args.notebook, temp_path / "briefing.md")
        map_id, diagram = get_mindmap(args.notebook, temp_path / "mindmap.json")
        briefing = insert_mindmap((temp_path / "briefing.md").read_text(encoding="utf-8-sig"), diagram)
        description = args.description or (
            f"Sintetiza as fontes de '{title}' em um briefing editorial com conclusões, mecanismos e aplicações, "
            "preservando proveniência permanente, conexões semânticas e um mapa mental nativo para recuperação no segundo cérebro."
        )
        data = {
            "type": "NotebookLM Summary",
            "title": title,
            "description": description,
            "tags": args.tag
            or [
                "area/gestao-do-conhecimento",
                "tema/sintese-de-fontes",
                "metodo/pesquisa-grounded",
                "sistema/segundo-cerebro",
                "ferramenta/notebooklm",
            ],
            "timestamp": now(),
            "notebook_id": args.notebook,
            "origin": "NotebookLM",
            "briefing_artifact_id": briefing_id,
            "mind_map_note_id": map_id,
            "knowledge_domains": args.knowledge_domain or ["gestao-do-conhecimento"],
            "neuron_links": args.neuron or [],
            "related_summaries": args.related_summary or [],
            "source_count": len(source_links),
            "source_links": source_links,
        }
        render(stage, title, slug, briefing, data)
        check = subprocess.run(
            [sys.executable, str(VALIDATOR), "--deck", str(stage), "--pt-br"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if check.returncode:
            raise RuntimeError("validação do staging falhou:\n" + check.stdout + check.stderr)
        if args.publish:
            publish(stage, args.deck, slug)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())