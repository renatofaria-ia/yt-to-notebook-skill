import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validar_nota.py"
FIXTURE = ROOT / "tests" / "fixtures" / "vault-minimalista-valido"


def run(deck: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--deck", str(deck), "--pt-br", *extra],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class ValidatorTests(unittest.TestCase):
    def copy_fixture(self, folder: str) -> Path:
        target = Path(folder) / "vault"
        shutil.copytree(FIXTURE, target)
        return target

    def summary(self, deck: Path) -> Path:
        return deck / "notebooks" / "curso-minimalista" / "curso-minimalista.md"

    def test_fixture_is_valid(self) -> None:
        result = run(FIXTURE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_evidence_directory(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            deck = self.copy_fixture(folder)
            (deck / "notebooks" / "curso-minimalista" / "evidence").mkdir()
            result = run(deck)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("evidence/ não é permitido", result.stdout)

    def test_rejects_root_index(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            deck = self.copy_fixture(folder)
            (deck / "index.md").write_text("# Índice\n", encoding="utf-8")
            result = run(deck)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("não permite índices", result.stdout)

    def test_rejects_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            deck = self.copy_fixture(folder)
            path = self.summary(deck)
            path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())
            result = run(deck)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("UTF-8 com BOM", result.stdout)

    def test_rejects_invalid_source_url(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            deck = self.copy_fixture(folder)
            path = self.summary(deck)
            path.write_text(path.read_text(encoding="utf-8").replace("https://example.com/fonte", "ftp://example.com/fonte"), encoding="utf-8")
            result = run(deck)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("URL de fonte inválida", result.stdout)

    def test_rejects_english_editorial_heading_in_pt_br_mode(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            deck = self.copy_fixture(folder)
            path = self.summary(deck)
            path.write_text(path.read_text(encoding="utf-8").replace("## 1. Sumário Executivo", "## 1. Executive Summary"), encoding="utf-8")
            result = run(deck)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Sumário Executivo", result.stdout)


if __name__ == "__main__":
    unittest.main()