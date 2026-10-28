"""Run: python3 -m unittest discover -s plugins/promo-video/skills/promo-video/tests  (no network)"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))
import pv_spec as S  # noqa: E402  # pyright: ignore[reportMissingImports]
import pv_voice as V  # noqa: E402  # pyright: ignore[reportMissingImports]

HAVE_MEDIA = bool(shutil.which("ffmpeg"))
R = None
try:
    import pv_render as R  # noqa: E402  # pyright: ignore[reportMissingImports]
    R.font_file("IBM Plex Sans", 600)
except Exception:  # PIL or fonts missing → skip the render tests only
    HAVE_MEDIA = False


def spec_from(d: dict, tmp: Path) -> dict:
    p = tmp / "video.json"
    p.write_text(json.dumps(d, ensure_ascii=False))
    return S.load(p)


def fake_timing(spec: dict, wps: float = 3.0, gap: float = .5) -> list[dict]:
    t, out = 0.0, []
    for sc in spec["scenes"]:
        ws = []
        for w in S.words(sc["say"]):
            ws.append([w, round(t, 3), round(t + 1 / wps - .05, 3)]); t += 1 / wps
        out.append({"id": sc["id"], "start": ws[0][1], "end": ws[-1][2], "words": ws}); t += gap
    return out


class Spec(unittest.TestCase):
    def test_find_word_handles_case_punctuation_cyrillic_and_nth(self):
        say = "Нажмите кнопку, и — нажмите снова! Where are we?"
        self.assertEqual(S.find_word(say, "кнопку"), 1)
        self.assertEqual(S.find_word(say, "Нажмите#2"), 4)
        self.assertEqual(S.find_word(say, "we"), 8)
        with self.assertRaises(KeyError):
            S.find_word(say, "нет")

    def test_validate_reports_missing_word_refs_and_bad_targets(self):
        with tempfile.TemporaryDirectory() as d:
            spec = spec_from({"targets": [{"platform": "tiktok", "format": "9:16"}],
                              "scenes": [{"id": "a", "type": "reveal", "say": "one two",
                                          "punch": {"text": "x", "at": "three"}},
                                         {"id": "a", "type": "nope", "say": "x"}]}, Path(d))
            problems = "\n".join(S.validate(spec))
        self.assertIn("'three' not found", problems)
        self.assertIn("duplicate id", problems)
        self.assertIn("type must be", problems)
        self.assertIn("platform must be", problems)

    def test_examples_are_valid(self):
        for p in sorted((SKILL / "examples").glob("*/video.json")):
            self.assertEqual(S.validate(S.load(p)), [], p.parent.name)

    def test_instagram_keeps_text_out_of_the_reels_ui(self):
        lay = S.layout("instagram", "9:16")
        self.assertLessEqual(lay["box"][3], .65)
        self.assertLessEqual(lay["caption_y"], .75)
        self.assertLessEqual(lay["caption_x"][1], .85, "right rail of buttons")


class Voice(unittest.TestCase):
    def test_scene_timing_maps_alignment_to_scenes_and_words(self):
        with tempfile.TemporaryDirectory() as d:
            spec = spec_from({"scenes": [{"id": "a", "type": "title", "say": "Привет, мир."},
                                         {"id": "b", "type": "title", "say": "Hit play"}]}, Path(d))
        text = S.script_text(spec)
        al = {"characters": list(text), "character_start_times_seconds": [i * .1 for i in range(len(text))],
              "character_end_times_seconds": [i * .1 + .09 for i in range(len(text))]}
        tm = V.scene_timing(spec, al)
        self.assertEqual([s["id"] for s in tm], ["a", "b"])
        self.assertEqual([w[0] for w in tm[1]["words"]], ["Hit", "play"])
        self.assertAlmostEqual(tm[1]["start"], text.index("Hit") * .1)
        self.assertAlmostEqual(tm[0]["end"], (len("Привет, мир.") - 1) * .1 + .09)

    def test_misheard_scores_and_lists_differences(self):
        wer, diffs = V.misheard("Grab it from the Bershadsky marketplace", "Grab it from the Bachinski marketplace")
        self.assertAlmostEqual(wer, 1 / 6)
        self.assertEqual(diffs, ["bershadsky → bachinski"])

    def test_best_prefers_accuracy_then_livelier_pitch(self):
        rows = [{"take": "a", "wer": .05, "pitch_range_st": 18}, {"take": "b", "wer": .01, "pitch_range_st": 12},
                {"take": "c", "wer": .012, "pitch_range_st": 15}]
        self.assertEqual(V.best(rows), "c")

    def test_settings_route_by_model_family(self):
        self.assertEqual(set(V.settings("eleven_v4", {"stability": .3})), {"stability"})
        self.assertIn("similarity_boost", V.settings("eleven_multilingual_v2", {}))

    def test_key_from_env_file_is_read_not_printed(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".env").write_text("OTHER=1\nexport ELEVENLABS_API_KEY='sk_test'\n")
            spec = spec_from({"voice": {"env_file": ".env"}, "scenes": []}, Path(d))
            import os
            old = os.environ.pop("ELEVENLABS_API_KEY", None)
            try:
                self.assertEqual(V.api_key(spec), "sk_test")
            finally:
                if old is not None: os.environ["ELEVENLABS_API_KEY"] = old


@unittest.skipUnless(HAVE_MEDIA, "needs ffmpeg, Pillow and IBM Plex fonts")
class Render(unittest.TestCase):
    def setUp(self):
        from PIL import Image
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        Image.new("RGB", (900, 500), "#335").save(d / "shot.png")
        self.spec = spec_from({
            "lang": "ru", "tail": .6,
            "targets": [{"platform": "instagram", "format": "9:16"}, {"platform": "telegram", "format": "1:1"}],
            "scenes": [
                {"id": "hook", "type": "reveal", "say": "Задачи в Jira и Linear. Где мы?", "lead": "Задачи в",
                 "items": [{"text": "Jira", "at": "Jira"}, {"text": "Linear", "at": "Linear"}], "punch": {"text": "Где мы?", "at": "где"}},
                {"id": "spot", "type": "spotlight", "say": "Длинный заголовок проверяет перенос строк.",
                 "title": "Очень длинный заголовок для проверки переноса", "image": "shot.png"},
                {"id": "map", "type": "mapping", "say": "Статусы приводятся к общей модели.",
                 "rows": [{"tag": "Jira", "left": "Code Review", "right": "in_review"}]},
                {"id": "cta", "type": "title", "say": "Одна команда.", "lines": ["promo-video"],
                 "code": {"lines": ["/plugin install promo-video@bershadsky-claude-tools"], "at": "команда"}}]}, d)
        self.timing = fake_timing(self.spec)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cuts_never_show_two_shots_and_captions_stay_in_their_shot(self):
        assert R is not None
        film = R.Film(self.spec, self.timing, "instagram", "9:16")
        self.assertTrue(all(v < .01 for v in film.cut_check()))
        b = film.ctx.bounds
        for start, end, ws in film.captions.chunks:
            i = max(j for j in range(len(b) - 1) if b[j] <= start)
            self.assertLessEqual(end, b[i + 1], ws)
        for start, end, ws in film.captions.chunks:
            self.assertLessEqual(film.captions.f.getlength(" ".join(w[0] for w in ws)), film.captions.maxw + 1)

    def test_cut_points_sit_in_the_silence_between_lines(self):
        assert R is not None
        film = R.Film(self.spec, self.timing, "telegram", "1:1")
        for (a, b), cut in zip(zip(self.timing, self.timing[1:]), film.ctx.bounds[1:-1]):
            self.assertTrue(a["end"] <= cut < b["start"])

    def test_encode_produces_video_with_audio(self):
        d = Path(self.tmp.name)
        vo = d / "vo.mp3"
        end = self.timing[-1]["end"]
        subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency=220:duration={end:.2f}", str(vo)], check=True)
        assert R is not None
        out = R.Film(self.spec, self.timing, "telegram", "1:1").encode(vo, d / "out.mp4", fps=6, workers=1)
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height", "-of", "json", str(out)],
                               capture_output=True, text=True).stdout
        streams = json.loads(probe)["streams"]
        self.assertEqual({s["codec_type"] for s in streams}, {"video", "audio"})
        self.assertEqual((streams[0]["width"], streams[0]["height"]), (1080, 1080))


if __name__ == "__main__":
    unittest.main()
