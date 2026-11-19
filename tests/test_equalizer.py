import unittest

from examples.equalizer import eq_matches, eq_payload


class EqualizerTests(unittest.TestCase):
    def setUp(self):
        self.settings = {
            "version": 1, "bass": 0, "treble": 2, "loudness": False,
            "night": False, "roomOn": True, "room": [{"hz": 90, "db": -2}],
        }

    def test_bass_edit_preserves_other_settings_and_copies_filters(self):
        result = eq_payload(self.settings, "bass", -3)
        self.assertEqual(result, {**self.settings, "bass": -3})
        result["room"][0]["hz"] = 120
        self.assertEqual(self.settings["room"][0]["hz"], 90)

    def test_accepts_tone_limits_and_boolean_switches(self):
        for key, value in [("bass", -12), ("treble", 12), ("night", True),
                           ("loudness", True)]:
            with self.subTest(key=key):
                self.assertEqual(eq_payload(self.settings, key, value)[key], value)

    def test_rejects_invalid_edits(self):
        for key, value in [("bass", True), ("bass", -13), ("treble", 1.5),
                           ("night", 1), ("loudness", "false"), ("room", [])]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                eq_payload(self.settings, key, value)

    def test_rejects_incomplete_settings(self):
        with self.assertRaises(ValueError):
            eq_payload({"bass": 0}, "bass", 2)

    def test_readback_accepts_empty_filter_normalization(self):
        self.assertTrue(eq_matches({**self.settings, "room": None},
                                   {**self.settings, "room": []}))
        self.assertFalse(eq_matches(self.settings, {**self.settings, "bass": 3}))
