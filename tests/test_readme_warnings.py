import os
import re
import unittest

from tests._loader import ROOT


def _readmes():
    paths = {"fr": os.path.join(ROOT, "README.md")}
    docs = os.path.join(ROOT, "docs")
    for name in sorted(os.listdir(docs)):
        found = re.fullmatch(r"README\.(\w+)\.md", name)
        if found:
            paths[found.group(1)] = os.path.join(docs, name)
    return paths


def _lines(path):
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


class ReadmeWarningsSectionTests(unittest.TestCase):
    def test_there_are_fifteen_readmes(self):
        self.assertEqual(len(_readmes()), 15)

    def test_section_comes_third_with_the_check_procedure(self):
        for code, path in _readmes().items():
            with self.subTest(lang=code):
                lines = _lines(path)
                heads = [i for i, l in enumerate(lines) if l.startswith("## ")]
                section = "\n".join(lines[heads[2]:heads[3]])
                for needle in ("SHA256SUMS.txt", "Get-FileHash", "Get-Content .\\SHA256SUMS.txt",
                               "-Algorithm SHA256", "OK", "DIFFERENT", "https://www.virustotal.com/",
                               "https://github.com/harlockSuites/YT-dlp-GUI/actions", "PowerShell", "Code signing policy"):
                    self.assertIn(needle, section)
                self.assertEqual(section.count("```"), 2, "un seul bloc de code : la commande de vérification")

    def test_the_command_is_identical_in_every_language(self):
        commands = set()
        for path in _readmes().values():
            lines = _lines(path)
            start = next(i for i, l in enumerate(lines) if l.startswith("Get-Content .\\SHA256SUMS.txt"))
            commands.add(lines[start])
        self.assertEqual(len(commands), 1, commands)

    def test_installation_section_keeps_its_own_code_block_and_ends_with_it(self):
        for code, path in _readmes().items():
            with self.subTest(lang=code):
                lines = _lines(path)
                heads = [i for i, l in enumerate(lines) if l.startswith("## ")]
                section = lines[heads[1]:heads[2]]
                self.assertIn("Get-FileHash .\\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256", section)
                last = [l for l in section if l.strip()][-1]
                self.assertEqual(last, "```", "plus de puce « Signaler un bogue » égarée après le bloc de code")

    def test_bug_report_section_has_its_two_bullets(self):
        for code, path in _readmes().items():
            with self.subTest(lang=code):
                lines = _lines(path)
                heads2 = [i for i, l in enumerate(lines) if l.startswith("## ")]
                bug = max(i for i, l in enumerate(lines) if l.startswith("### ") and i < heads2[1])
                bullets = [l for l in lines[bug:heads2[1]] if l.startswith("- ")]
                self.assertEqual(len(bullets), 2)
                self.assertIn("GitHub", bullets[0])

    def test_blank_line_before_each_heading(self):
        for code, path in _readmes().items():
            with self.subTest(lang=code):
                lines = _lines(path)
                for i, l in enumerate(lines):
                    if l.startswith("## ") and i > 0:
                        self.assertEqual(lines[i - 1].strip(), "", f"ligne {i + 1} : {l[:40]}")


if __name__ == "__main__":
    unittest.main()
