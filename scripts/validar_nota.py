#!/usr/bin/env python3
"""Valida a estrutura minimalista do vault notebooklm-to-notes."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


def read(path: Path, errors: list[str]) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{path}: UTF-8 com BOM")
    try:
        text = raw.decode("utf-8").replace("\r\n", "\n")
    except UnicodeDecodeError as error:
        errors.append(f"{path}: não é UTF-8 válido: {error}")
        return ""
    if chr(195) in text or chr(65533) in text:
        errors.append(f"{path}: contém mojibake")
    return text


def parse(text: str, path: Path, errors: list[str]) -> tuple[dict[str, Any], str]:
    match = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", text, re.DOTALL)
    if not match:
        errors.append(f"{path}: frontmatter YAML ausente")
        return {}, text
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as error:
        errors.append(f"{path}: YAML inválido: {error}")
        return {}, match.group(2)
    return data if isinstance(data, dict) else {}, match.group(2)


def exists(vault: Path, link: Any) -> bool:
    return isinstance(link, str) and link.startswith("/") and (vault / link[1:]).is_file()


def check_pt_br(body: str, path: Path, errors: list[str]) -> None:
    forbidden = re.compile(r"^## (?:1\. Executive Summary|Mind Map|Original Sources)\s*$", re.MULTILINE)
    if forbidden.search(body):
        errors.append(f"{path}: --pt-br exige cabeçalhos editoriais em português")


def check_summary(vault: Path, folder: Path, errors: list[str], pt_br: bool) -> None:
    slug = folder.name
    path = folder / f"{slug}.md"
    if not path.is_file():
        errors.append(f"{folder}: resumo ausente")
        return
    data, body = parse(read(path, errors), path, errors)
    for key in ("notebook_id", "briefing_artifact_id", "mind_map_note_id", "source_count", "source_links"):
        if not data.get(key):
            errors.append(f"{path}: exige {key}")
    if not isinstance(data.get("description"), str) or not 180 <= len(data["description"]) <= 320:
        errors.append(f"{path}: description deve ter 180-320 caracteres")
    tags = data.get("tags")
    if not isinstance(tags, list) or not 4 <= len(tags) <= 8 or any(not isinstance(tag, str) or "/" not in tag for tag in tags):
        errors.append(f"{path}: exige 4-8 tags hierárquicas")
    source_links = data.get("source_links")
    if not isinstance(source_links, list) or data.get("source_count") != len(source_links):
        errors.append(f"{path}: source_count incompatível com source_links")
    else:
        for source in source_links:
            if not isinstance(source, dict) or not all(source.get(key) for key in ("title", "type", "notebooklm_source_id")):
                errors.append(f"{path}: fonte sem título, tipo ou ID")
                continue
            url = source.get("url")
            if url is not None and (not isinstance(url, str) or not re.match(r"https?://", url)):
                errors.append(f"{path}: URL de fonte inválida")
            if isinstance(url, str) and url not in body:
                errors.append(f"{path}: URL da fonte não está no corpo")
    executive = re.search(r"^## 1\. Sumário Executivo\s*$", body, re.MULTILINE)
    map_heading = re.search(r"^## Mapa mental\s*$", body, re.MULTILINE)
    second = re.search(r"^## 2\. ", body, re.MULTILINE)
    if not executive or not map_heading or not second or not executive.start() < map_heading.start() < second.start():
        errors.append(f"{path}: mapa mental deve ficar após Sumário Executivo e antes da seção 2")
    elif body.count("## Mapa mental") != 1:
        errors.append(f"{path}: exige exatamente um mapa mental")
    else:
        tick = chr(96) * 3
        if tick + "mermaid\nmindmap\n" not in body:
            errors.append(f"{path}: Mermaid mindmap inválido")
    if "evidence/" in body:
        errors.append(f"{path}: não pode referenciar evidence/")
    if "## Fontes originais" not in body:
        errors.append(f"{path}: seção Fontes originais ausente")
    if pt_br:
        check_pt_br(body, path, errors)
    for link in data.get("neuron_links", []):
        if not exists(vault, link):
            errors.append(f"{path}: neurônio inexistente: {link}")
    for link in data.get("related_summaries", []):
        if not exists(vault, link):
            errors.append(f"{path}: resumo relacionado inexistente: {link}")


def validate(vault: Path, pt_br: bool = False) -> list[str]:
    errors: list[str] = []
    if not (vault / "neurons").is_dir() or not (vault / "notebooks").is_dir():
        return ["vault exige neurons/ e notebooks/"]
    if any((vault / name).exists() for name in ("index.md", "log.md")) or (vault / "notebooks" / "index.md").exists():
        errors.append("vault minimalista não permite índices ou log na raiz")
    for path in vault.rglob("*"):
        if path.is_dir() and path.name == "evidence":
            errors.append(f"{path}: evidence/ não é permitido")
        if path.is_file() and path.suffix.lower() in {".md", ".json"}:
            read(path, errors)
    for folder in (vault / "notebooks").iterdir():
        if folder.is_dir():
            if not (folder / "index.md").is_file() or not (folder / "log.md").is_file():
                errors.append(f"{folder}: exige index.md e log.md")
            check_summary(vault, folder, errors, pt_br)
    return errors


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--deck", required=True, type=Path)
    parser.add_argument("--pt-br", action="store_true")
    args = parser.parse_args()
    failures = validate(args.deck, args.pt_br)
    print("\n".join(f"ERRO {item}" for item in failures) if failures else "OK vault minimalista válido")
    raise SystemExit(1 if failures else 0)