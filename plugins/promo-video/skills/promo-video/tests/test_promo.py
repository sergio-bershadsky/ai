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
import pv_master as M  # noqa: E402  # pyright: ignore[reportMissingImports]
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

    def test_reading_need_is_a_floor_for_short_lines_and_scales_with_words(self):
        self.assertAlmostEqual(S.reading_need("Где мы?"), .8)
        self.assertAlmostEqual(S.reading_need("one two three four five"), 1.5)
        self.assertEqual(S.reading_need("   "), 0)
        self.assertAlmostEqual(S.reading_need("Linear · Jira · monday.com · GitHub · …"), 1.2, msg="separators are not words")

    def test_reading_floor_flags_a_punch_that_lands_on_the_last_word(self):
        with tempfile.TemporaryDirectory() as d:
            spec = spec_from({"tail": .3, "scenes": [
                {"id": "hook", "type": "reveal", "say": "Tasks live everywhere. So where are we now",
                 "lead": "Tasks live", "items": [{"text": "everywhere", "at": "everywhere"}],
                 "punch": {"text": "So where are we now, really, today?", "at": "now"}}]}, Path(d))
            problems = S.reading_problems(spec, fake_timing(spec))
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("hook", problems[0])
        self.assertIn("punch", problems[0])

    def test_reading_floor_counts_reveal_items_only_until_the_punch_dims_them(self):
        with tempfile.TemporaryDirectory() as d:
            spec = spec_from({"scenes": [
                {"id": "hook", "type": "reveal", "say": "Jira Linear GitHub and then where are we in all of this",
                 "items": [{"text": "Jira and its many many workflow states", "at": "GitHub"}],
                 "punch": {"text": "Where?", "at": "and"}}]}, Path(d))
            problems = S.reading_problems(spec, fake_timing(spec))
        self.assertTrue(any("items[0]" in p for p in problems), problems)

    def test_examples_are_readable_at_the_measured_narration_rate(self):
        # 2.2 words/s is the fast end measured on eleven_v4 (SKILL.md, word budget)
        for p in sorted((SKILL / "examples").glob("*/video.json")):
            spec = S.load(p)
            self.assertEqual(S.reading_problems(spec, fake_timing(spec, wps=2.2)), [], p.parent.name)


class Master(unittest.TestCase):
    def test_accept_passes_a_compliant_master(self):
        m = {"I": -14.2, "TP": -1.3}
        self.assertEqual(M.accept(m, dur_v=20.0, dur_a=20.02), [])

    def test_accept_names_every_failed_item(self):
        problems = "\n".join(M.accept({"I": -17.0, "TP": -0.2}, dur_v=20.0, dur_a=19.5))
        self.assertIn("loudness", problems)
        self.assertIn("true peak", problems)
        self.assertIn("duration", problems)

    @unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
    def test_master_brings_a_quiet_mix_to_target(self):
        with tempfile.TemporaryDirectory() as d:
            src, dst = Path(d) / "mix.wav", Path(d) / "master.wav"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=220:duration=6",
                            "-af", "volume=-32dB", str(src)], check=True)
            M.master_wav(src, dst)
            m = M.measure(dst)
        self.assertLessEqual(abs(m["I"] - M.TARGET_I), M.TOL_I, m)
        self.assertLessEqual(m["TP"], M.TARGET_TP, m)


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

    def _vo(self) -> Path:
        vo = Path(self.tmp.name) / "vo.mp3"
        if not vo.exists():
            end = self.timing[-1]["end"]
            subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency=220:duration={end:.2f}",
                            "-af", "volume=-26dB", str(vo)], check=True)
        return vo

    def _streams(self, out: Path) -> list[dict]:
        probe = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_entries",
                                "stream=codec_type,width,height,nb_read_frames:stream_disposition=attached_pic",
                                "-of", "json", str(out)], capture_output=True, text=True).stdout
        return json.loads(probe)["streams"]

    def test_encode_produces_a_mastered_video_with_audio(self):
        assert R is not None
        fps = 6
        film = R.Film(self.spec, self.timing, "telegram", "1:1")
        out = film.encode(self._vo(), Path(self.tmp.name) / "out.mp4", fps=fps, workers=1)
        streams = self._streams(out)
        self.assertEqual({s["codec_type"] for s in streams}, {"video", "audio"})
        video = next(s for s in streams if s["codec_type"] == "video")
        self.assertEqual((video["width"], video["height"]), (1080, 1080))
        self.assertEqual(int(video["nb_read_frames"]), int(film.ctx.end * fps))
        self.assertEqual(M.check(out), [])

    def test_frame_zero_is_the_settled_cover_not_an_empty_background(self):
        import numpy as np
        assert R is not None
        film = R.Film(self.spec, self.timing, "telegram", "1:1")
        f0 = np.asarray(film.frame_at(0, 30), np.float32)
        self.assertGreater(np.abs(f0 - np.asarray(film.bg_rgb, np.float32)).mean(), 1.0, "frame 0 is blank")
        self.assertTrue(np.array_equal(f0, np.asarray(film.frame(film.cover_t), np.float32)))
        self.assertLess(film.cover_t, film.ctx.bounds[1], "the cover comes from the first scene by default")
        self.spec["cover"] = False
        bare = R.Film(self.spec, self.timing, "telegram", "1:1")
        self.assertTrue(np.array_equal(np.asarray(bare.frame_at(0, 30)), np.asarray(bare.frame(0))))

    def test_cover_can_be_embedded_as_attached_picture(self):
        assert R is not None
        self.spec["cover"] = {"embed": True}
        out = R.Film(self.spec, self.timing, "telegram", "1:1").encode(self._vo(), Path(self.tmp.name) / "c.mp4", fps=6, workers=1)
        self.assertTrue(any(s.get("disposition", {}).get("attached_pic") for s in self._streams(out)))
        self.assertTrue((Path(self.tmp.name) / "c.cover.jpg").exists())

    def test_rerender_redraws_only_the_chunks_of_the_changed_scene(self):
        assert R is not None
        d, fps = Path(self.tmp.name), 6
        film = R.Film(self.spec, self.timing, "telegram", "1:1")
        film.encode(self._vo(), d / "inc.mp4", fps=fps, workers=1)
        everything = set(film.rendered)
        self.assertEqual(everything, set(range(len(film.chunks(fps)))))

        again = R.Film(self.spec, self.timing, "telegram", "1:1")
        again.encode(self._vo(), d / "inc.mp4", fps=fps, workers=1)
        self.assertEqual(again.rendered, [], "nothing changed, nothing redrawn")

        self.spec["scenes"][2]["sub"] = "A late fix to one card"
        fixed = R.Film(self.spec, self.timing, "telegram", "1:1")
        out = fixed.encode(self._vo(), d / "inc.mp4", fps=fps, workers=1)
        b = fixed.ctx.bounds
        touched = {i for i, (k0, k1) in enumerate(fixed.chunks(fps)) if k0 / fps < b[3] and k1 / fps > b[2]}
        self.assertTrue(fixed.rendered)
        self.assertLessEqual(set(fixed.rendered), touched)
        self.assertLess(len(fixed.rendered), len(everything))
        video = next(s for s in self._streams(out) if s["codec_type"] == "video")
        self.assertEqual(int(video["nb_read_frames"]), int(fixed.ctx.end * fps))


if __name__ == "__main__":
    unittest.main()
