import json
import os
import socket
import ssl
import unittest
import urllib.error

from tests._loader import load_gui

m = load_gui()

LANG_DIR = os.path.join(os.path.dirname(m.__file__), "lang")
ACCOUNT_WORD = {"fr": "compte", "en": "account", "es": "cuenta", "pt": "conta", "it": "account", "pl": "kont",
                "hu": "fiók", "ru": "аккаунт", "sr": "nalog", "vi": "tài khoản", "fil": "account", "hi": "खाता",
                "ja": "アカウント", "ko": "계정", "zh": "账号"}


class NetworkErrorTests(unittest.TestCase):
    def setUp(self):
        m.load_lang("fr")

    def test_no_internet_is_explained(self):
        gai = socket.gaierror(11001, "getaddrinfo failed")
        for exc in (gai, urllib.error.URLError(gai)):
            text = m.describe_network_error(exc)
            self.assertIn("Pas de connexion à Internet", text)
            self.assertIn("getaddrinfo failed", text, "le détail technique reste disponible")

    def test_timeouts_are_explained(self):
        for exc in (TimeoutError("timed out"), urllib.error.URLError(socket.timeout("timed out"))):
            self.assertIn("ne répond pas", m.describe_network_error(exc))

    def test_refused_or_blocked_connections_are_explained(self):
        for exc in (ConnectionRefusedError(10061, "refusé"), ConnectionResetError(10054, "réinitialisée"),
                    urllib.error.URLError(ssl.SSLError("handshake"))):
            self.assertIn("Impossible de joindre le serveur", m.describe_network_error(exc))

    def test_other_errors_are_left_alone(self):
        self.assertIsNone(m.describe_network_error(ValueError("autre chose")))
        self.assertIsNone(m.describe_network_error(PermissionError(13, "refusé")))

    def test_update_check_without_internet_gives_the_clear_message(self):
        def offline(*_a, **_k):
            raise urllib.error.URLError(socket.gaierror(11001, "getaddrinfo failed"))
        with self.assertRaises(m.UpdateError) as caught:
            m.fetch_latest_release(opener=offline)
        self.assertIn("Pas de connexion à Internet", str(caught.exception))
        self.assertNotIn("[Errno", str(caught.exception).split("(Détail")[0])

    def test_http_errors_keep_their_own_message(self):
        def not_found(*_a, **_k):
            raise urllib.error.HTTPError("https://api.github.com", 404, "Not Found", {}, None)
        with self.assertRaises(m.UpdateError) as caught:
            m.fetch_latest_release(opener=not_found)
        self.assertTrue(caught.exception.not_found)

    def test_every_language_has_the_three_texts_with_a_detail_placeholder(self):
        for name in sorted(os.listdir(LANG_DIR)):
            with self.subTest(lang=name):
                with open(os.path.join(LANG_DIR, name), encoding="utf-8") as f:
                    texts = json.load(f)
                for key in ("net.offline", "net.timeout", "net.unreachable"):
                    self.assertIn("{detail}", texts[key], key)


class BugFormMentionsGithubAccountTests(unittest.TestCase):
    def test_intro_says_a_github_account_is_needed_in_every_language(self):
        for code, word in ACCOUNT_WORD.items():
            with self.subTest(lang=code):
                with open(os.path.join(LANG_DIR, f"{code}.json"), encoding="utf-8") as f:
                    intro = json.load(f)["bug.intro"]
                self.assertIn("GitHub", intro)
                self.assertIn(word, intro.lower() if code not in ("hi", "ja", "ko", "zh") else intro)

    def test_the_french_sentence_is_exact(self):
        with open(os.path.join(LANG_DIR, "fr.json"), encoding="utf-8") as f:
            self.assertIn("compte GitHub gratuit", json.load(f)["bug.intro"])

    def test_readme_bug_section_mentions_it_in_every_language(self):
        root = os.path.dirname(m.__file__)
        paths = {"fr": os.path.join(root, "README.md")}
        for code in ACCOUNT_WORD:
            if code != "fr":
                paths[code] = os.path.join(root, "docs", f"README.{code}.md")
        for code, path in paths.items():
            with self.subTest(lang=code):
                with open(path, encoding="utf-8") as f:
                    lines = f.read().splitlines()
                install = [i for i, l in enumerate(lines) if l.startswith("## ")][1]
                bug = max(i for i, l in enumerate(lines) if l.startswith("### ") and i < install)
                bullet = next(l for l in lines[bug:install] if l.startswith("- "))
                self.assertIn("GitHub", bullet)
                self.assertIn(ACCOUNT_WORD[code], bullet.lower() if code not in ("hi", "ja", "ko", "zh") else bullet)


if __name__ == "__main__":
    unittest.main()
