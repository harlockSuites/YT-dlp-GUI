import re
import unittest

from tests._loader import load_gui, tk_available

m = load_gui()


class MultiAudioArgsTests(unittest.TestCase):
    def test_multi_audio_always_asks_yt_dlp_to_tag_the_language_of_each_track(self):
        args = m.MULTI_AUDIO_ARGS
        self.assertIn("--audio-multistreams", args)
        self.assertIn("--embed-metadata", args, "sans lui, les pistes n'ont pas d'étiquette de langue")
        self.assertEqual(args[-2:], ["--merge-output-format", "mkv"])

    def test_no_builder_adds_multistreams_without_the_metadata_flag(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        literal = re.findall(r'^.*"--audio-multistreams".*$', source, re.M)
        # constante MULTI_AUDIO_ARGS, bloc « Multi-pistes audio (MKV) », liste des options critiques
        self.assertEqual(len(literal), 3, literal)
        for line in literal:
            self.assertIn('"--embed-metadata"', line)

    def test_script_block_keeps_the_tags_too(self):
        block = m.SCRIPT_BLOCKS_MAP["audio_multistream"]
        self.assertIn("--embed-metadata", block)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class MainWindowArgsTests(unittest.TestCase):
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

    def test_secondary_tracks_produce_a_tagged_mkv(self):
        self.app._secondary_sel.set_selected(["alang_en"])
        args = self.app._build_args()
        self.assertIn("--audio-multistreams", args)
        self.assertIn("--embed-metadata", args)
        self.assertEqual(args[args.index("--merge-output-format") + 1], "mkv")

    def test_audio_only_with_secondary_tracks_is_tagged_too(self):
        self.app.var_audio_only.set(True)
        self.app._secondary_sel.set_selected(["alang_en"])
        args = self.app._build_args()
        self.assertIn("--audio-multistreams", args)
        self.assertIn("--embed-metadata", args)

    def test_single_track_downloads_are_left_unchanged(self):
        args = self.app._build_args()
        self.assertNotIn("--audio-multistreams", args)
        self.assertNotIn("--embed-metadata", args)


if __name__ == "__main__":
    unittest.main()
