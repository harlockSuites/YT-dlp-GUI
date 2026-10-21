import unittest

from tests._loader import load_gui

m = load_gui()

# sortie réelle de `yt-dlp -F` (abrégée) pour une vidéo sans langue déclarée dans le JSON
NO_LANGUAGE = """\
[youtube] J7Nb13oYwjc: Downloading webpage
[youtube] [jsc:deno] Solving JS challenges using deno
[info] Available formats for J7Nb13oYwjc:
ID      EXT   RESOLUTION FPS CH |   FILESIZE   TBR PROTO | VCODEC          VBR ACODEC      ABR ASR MORE INFO
-------------------------------------------------------------------------------------------------------------
sb0     mhtml 160x90       1    |                   mhtml | images                                  storyboard
251     webm  audio only      2 |    1.83MiB  130k https | audio only          opus       130k 48k medium, webm_dash
137     mp4   1920x1080    30    |   20.00MiB 2500k https | avc1.640028    2500k video only          1080p, mp4_dash
"""

WITH_LANGUAGES = """\
[info] Available formats for abc:
ID  EXT  RESOLUTION FPS CH |   FILESIZE   TBR PROTO | VCODEC  VBR ACODEC   ABR ASR MORE INFO
-----------------------------------------------------------------------------------------
140-0 m4a audio only    2 |    3.00MiB  129k https | audio only      mp4a.40.2 129k 44k [en] medium
140-1 m4a audio only    2 |    3.00MiB  129k https | audio only      mp4a.40.2 129k 44k [fr] medium
140-2 m4a audio only    2 |    3.00MiB  129k https | audio only      mp4a.40.2 129k 44k [und] medium
18    mp4  640x360     30  2 | 14.47MiB  540k https | avc1.42001E mp4a.40.2   44k [es] 360p
"""


class FormatTableLanguagesTests(unittest.TestCase):
    def test_info_line_is_not_a_language(self):
        """« Pistes audio : info » : la ligne « [info] Available formats… » était lue comme un code de langue."""
        self.assertEqual(m.format_table_languages(NO_LANGUAGE), set())

    def test_languages_come_from_the_table_rows_only(self):
        self.assertEqual(m.format_table_languages(WITH_LANGUAGES), {"en", "fr", "es"})

    def test_undefined_language_is_ignored(self):
        self.assertNotIn("und", m.format_table_languages(WITH_LANGUAGES))

    def test_empty_or_error_output_gives_nothing(self):
        self.assertEqual(m.format_table_languages(""), set())
        self.assertEqual(m.format_table_languages("ERROR: [youtube] J7Nb13oYwjc: Video unavailable"), set())

    def test_main_window_uses_it(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        self.assertIn("audio_langs.update(format_table_languages(r2.stdout))", source)


if __name__ == "__main__":
    unittest.main()
