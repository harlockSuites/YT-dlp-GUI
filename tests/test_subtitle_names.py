import os

from tests.test_gui import GuiCase, VID, _opt, m


class SeparateSubtitleNamesTests(GuiCase):
    """Les sous-titres non intégrés doivent porter exactement le nom de la vidéo (numérotation, _2, _3…)."""

    def setUp(self):
        super().setUp()
        self.insp = m.PlaylistInspectorWindow(self.app, outdir=self.out)
        self.insp.withdraw()
        self.addCleanup(self.insp.destroy)
        self.insp._g_subs.set_options([("fr", "FR")])
        self.insp._g_subs.set_selected(["fr"])
        self.insp.var_g_embed_subs.set(False)

    def _row(self, vid=None):
        self.insp._clear_rows()
        self.insp._add_row(1, dict(vid or VID))
        return self.insp._rows[0]

    def test_numbering_prefix_is_kept(self):
        self.insp.var_g_numbering.set(True)
        row = self._row()
        video = self.insp._build_video_args(row)
        subs = self.insp._build_video_args(row, subs_only=True)
        self.assertTrue(os.path.basename(_opt(video, "-o")).startswith("01 - "))
        self.assertEqual(_opt(subs, "-o"), _opt(video, "-o"))

    def test_conflict_suffix_is_kept_even_after_the_video_exists(self):
        open(os.path.join(self.out, "Ma vidéo.mp4"), "w").close()      # une vidéo du même nom est déjà là
        row = self._row()
        video = self.insp._build_video_args(row)
        self.assertEqual(os.path.basename(_opt(video, "-o")), "Ma vidéo_2.%(ext)s")
        open(os.path.join(self.out, "Ma vidéo_2.mkv"), "w").close()    # ... puis la vidéo est téléchargée
        subs = self.insp._build_video_args(row, subs_only=True)
        self.assertEqual(os.path.basename(_opt(subs, "-o")), "Ma vidéo_2.%(ext)s")

    def test_plain_name_when_there_is_no_numbering_or_conflict(self):
        row = self._row()
        video = self.insp._build_video_args(row)
        subs = self.insp._build_video_args(row, subs_only=True)
        self.assertEqual(_opt(subs, "-o"), _opt(video, "-o"))

    def test_without_a_previous_video_pass_the_old_template_is_used(self):
        row = self._row()
        row.pop("_out_template", None)
        subs = self.insp._build_video_args(row, subs_only=True)
        self.assertEqual(os.path.basename(_opt(subs, "-o")), "%(title)s.%(ext)s")
