import unittest

from tests._loader import load_gui, tk_available

m = load_gui()


class EmbedSubsConstantTests(unittest.TestCase):
    def test_embedding_always_asks_for_the_authors_subtitles_too(self):
        args = m.EMBED_SUBS_ARGS
        # sans --write-subs, « --write-auto-subs --embed-subs » ne cherche que les sous-titres automatiques
        self.assertIn("--write-subs", args)
        self.assertIn("--embed-subs", args)
        self.assertEqual(args[-2:], ["--compat-options", "no-keep-subs"], "pas de .srt laissés à côté du fichier")

    def test_no_builder_embeds_subtitles_without_the_constant(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        self.assertEqual(source.count('["--embed-subs"]'), 0)
        self.assertEqual(source.count("args += EMBED_SUBS_ARGS"), 3)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class MainWindowSubtitleArgsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.app.var_audio_only.set(False)
        self.app._secondary_sel.set_selected([])
        self.app._subs_sel.set_selected(["alang_en", "alang_fr"])

    def tearDown(self):
        self.app._subs_sel.set_selected([])
        self.app.var_embed_subs.set(False)

    def test_embedded_subtitles_request_both_kinds(self):
        self.app.var_embed_subs.set(True)
        args = self.app._build_args()
        for flag in ("--write-subs", "--write-auto-subs", "--embed-subs"):
            self.assertIn(flag, args)
        self.assertEqual(args[args.index("--compat-options") + 1], "no-keep-subs")
        self.assertEqual(args[args.index("--sub-lang") + 1], "en,fr")

    def test_embedded_subtitles_with_secondary_audio(self):
        self.app.var_embed_subs.set(True)
        self.app._secondary_sel.set_selected(["alang_es"])
        args = self.app._build_args()
        self.assertIn("--write-subs", args)
        self.assertIn("--embed-subs", args)
        self.assertIn("--embed-metadata", args)
        self.assertEqual(args[args.index("--merge-output-format") + 1], "mkv")

    def test_separate_subtitle_files_are_unchanged(self):
        self.app.var_embed_subs.set(False)
        args = self.app._build_args()
        self.assertIn("--write-subs", args)
        self.assertIn("--write-auto-subs", args)
        self.assertNotIn("--embed-subs", args)
        self.assertNotIn("--compat-options", args)


if __name__ == "__main__":
    unittest.main()
