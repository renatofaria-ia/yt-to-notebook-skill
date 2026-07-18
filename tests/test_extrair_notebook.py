import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("extractor", ROOT / "scripts" / "extrair_notebook.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ExtractorTests(unittest.TestCase):
    def diagram(self) -> str:
        return MODULE.mindmap_mermaid({"title": "Memória", "children": [{"title": "Técnicas", "children": [{"title": "Integração"}]}]})

    def test_slug_and_mermaid_keep_accents(self) -> None:
        self.assertEqual(MODULE.slugify("Síntese: Claude & NotebookLM"), "sintese-claude-notebooklm")
        self.assertEqual(MODULE.find_id({"task_id": "artifact-1"}), "artifact-1")
        self.assertIn("Técnicas", self.diagram())

    def test_mindmap_is_downloaded_after_generation(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "mindmap.json"
            calls: list[list[str]] = []

            def fake_cli(args: list[str]) -> bytes:
                calls.append(args)
                if args[:2] == ["download", "mind-map"]:
                    output.write_text(json.dumps({"title": "Mapa", "children": [{"title": "Nó"}]}, ensure_ascii=False), encoding="utf-8")
                return b""

            with patch.object(MODULE, "request", return_value={"artifact_id": "map-1"}), patch.object(MODULE, "wait"), patch.object(MODULE, "cli", side_effect=fake_cli):
                artifact, diagram = MODULE.get_mindmap("notebook-1", output)

            self.assertEqual(artifact, "map-1")
            self.assertIn("root((Mapa))", diagram)
            self.assertTrue(any(args[:2] == ["download", "mind-map"] and "--artifact" in args for args in calls))

    def test_publish_creates_minimal_vault_from_empty_destination(self) -> None:
        briefing = "## 1. Sumário Executivo\n\nResumo validado.\n\n## 2. Aplicações\n\nDetalhes.\n"
        sources = [{"title": "Fonte técnica", "url": "https://example.com/fonte", "type": "web_page", "notebooklm_source_id": "source-1"}]
        with tempfile.TemporaryDirectory() as folder:
            vault = Path(folder) / "vault"
            argv = ["extrair_notebook.py", "--notebook", "notebook-1", "--deck", str(vault), "--publish"]
            def fake_get_report(notebook: str, output: Path) -> str:
                output.write_text(briefing, encoding="utf-8")
                return "briefing-1"

            with patch.object(sys, "argv", argv), patch.object(MODULE, "sources", return_value=("Curso de teste", sources)), patch.object(MODULE, "get_report", side_effect=fake_get_report), patch.object(MODULE, "get_mindmap", return_value=("map-1", self.diagram())):
                self.assertEqual(MODULE.main(), 0)

            summary = vault / "notebooks" / "curso-de-teste" / "curso-de-teste.md"
            self.assertTrue((vault / "neurons").is_dir())
            self.assertTrue(summary.is_file())
            self.assertTrue((vault / ".obsidian" / "graph.json").is_file())
            self.assertIn("## Mapa mental", summary.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()