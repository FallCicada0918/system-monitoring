import sys
import unittest
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cyber_pulse.i18n import (
    t, set_language, get_language, next_language,
    detect_system_language, LANGUAGE_NAMES,
    LANG_ZH_CN, LANG_ZH_TW, LANG_EN, LANG_JA, SUPPORTED_LANGUAGES
)


class TestI18n(unittest.TestCase):
    def setUp(self):
        set_language(LANG_ZH_CN)

    def test_supported_languages(self):
        self.assertIn(LANG_ZH_CN, SUPPORTED_LANGUAGES)
        self.assertIn(LANG_ZH_TW, SUPPORTED_LANGUAGES)
        self.assertIn(LANG_EN, SUPPORTED_LANGUAGES)
        self.assertIn(LANG_JA, SUPPORTED_LANGUAGES)
        self.assertEqual(len(SUPPORTED_LANGUAGES), 4)

    def test_title_translations(self):
        self.assertEqual(t("title", LANG_ZH_CN), "机体生命征象诊断仪")
        self.assertEqual(t("title", LANG_ZH_TW), "機體生命徵象診斷儀")
        self.assertEqual(t("title", LANG_EN), "Somatic Vital Signs Diagnostic Monitor")
        self.assertEqual(t("title", LANG_JA), "機体生命兆候診断装置")

    def test_language_switching(self):
        set_language(LANG_EN)
        self.assertEqual(get_language(), LANG_EN)
        self.assertEqual(t("title"), "Somatic Vital Signs Diagnostic Monitor")

        set_language(LANG_JA)
        self.assertEqual(get_language(), LANG_JA)
        self.assertEqual(t("title"), "機体生命兆候診断装置")

        set_language(LANG_ZH_TW)
        self.assertEqual(get_language(), LANG_ZH_TW)
        self.assertEqual(t("title"), "機體生命徵象診斷儀")

        set_language(LANG_ZH_CN)
        self.assertEqual(get_language(), LANG_ZH_CN)
        self.assertEqual(t("title"), "机体生命征象诊断仪")

    def test_next_language_cycle(self):
        set_language(LANG_ZH_CN)
        lang2 = next_language()
        self.assertEqual(lang2, LANG_ZH_TW)
        lang3 = next_language()
        self.assertEqual(lang3, LANG_EN)
        lang4 = next_language()
        self.assertEqual(lang4, LANG_JA)
        lang1 = next_language()
        self.assertEqual(lang1, LANG_ZH_CN)

    def test_fallback_behavior(self):
        # Non-existent key should return the key itself
        self.assertEqual(t("non_existent_key_12345"), "non_existent_key_12345")


if __name__ == "__main__":
    unittest.main()
