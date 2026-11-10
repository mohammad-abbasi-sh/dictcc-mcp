"""Offline tests — parse real captured dict.cc pages (scripts/styles
stripped), no network."""
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from dictcc_mcp import domain as dom
from dictcc_mcp import server as srv

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"


def _read(name):
    return (FIX / name).read_text(encoding="utf-8")


class TestValidation(unittest.TestCase):
    def test_pair(self):
        self.assertEqual(dom.validate_pair("de-fr"), "de-fr")
        self.assertEqual(dom.validate_pair("DE-EN"), "de-en")
        self.assertEqual(dom.validate_pair(""), "de-en")
        for bad in ["en-de", "de-de", "xx-yy", "leo"]:
            with self.assertRaises(ValueError, msg=bad):
                dom.validate_pair(bad)

    def test_pair_count(self):
        self.assertEqual(len(dom.PAIRS), 23)

    def test_query_and_limit(self):
        self.assertEqual(dom.validate_query("  Haus "), "Haus")
        with self.assertRaises(ValueError):
            dom.validate_query("")
        self.assertEqual(dom.validate_limit(10), 10)
        with self.assertRaises(ValueError):
            dom.validate_limit(51)

    def test_pair_url(self):
        self.assertEqual(dom.pair_url("de-en", "Haus"),
                         "https://www.dict.cc/?s=Haus")
        self.assertEqual(dom.pair_url("de-fr", "Haus"),
                         "https://defr.dict.cc/?s=Haus")


class TestTableHaus(unittest.TestCase):
    def setUp(self):
        self.items = dom.parse_table(_read("trans-haus.html"), "en")

    def test_row_count(self):
        self.assertEqual(len(self.items), 50)

    def test_first_row(self):
        self.assertEqual(self.items[0], {
            "german": "Haus-", "german_info": "[z. B. Schwein, Müll, Arbeit]",
            "en": "domestic", "en_info": "{adj} [e.g. pig, waste, work]",
            "votes": 558})

    def test_noun_row(self):
        row = self.items[8]
        self.assertEqual(row["german"], "Haus")
        self.assertEqual(row["german_info"], "{n} [Zuhause, Heim]")
        self.assertEqual(row["en"], "home")
        self.assertEqual(row["votes"], 154)

    def test_direction(self):
        self.assertEqual(dom.detect_direction(self.items, "Haus", "en"), "de")


class TestTableOther(unittest.TestCase):
    def test_laufen(self):
        items = dom.parse_table(_read("trans-laufen.html"), "en")
        self.assertEqual(len(items), 50)
        self.assertEqual(items[0]["german"], "laufen")
        self.assertEqual(items[0]["en"], "run")
        self.assertEqual(items[0]["votes"], 4099)
        self.assertEqual(dom.detect_direction(items, "laufen", "en"), "de")

    def test_house_english_direction(self):
        items = dom.parse_table(_read("trans-house.html"), "en")
        self.assertEqual(len(items), 50)
        self.assertEqual(items[0]["en"], "house")
        self.assertEqual(dom.detect_direction(items, "house", "en"), "en")

    def test_french_pair(self):
        items = dom.parse_table(_read("trans-haus-fr.html"), "fr")
        self.assertEqual(len(items), 39)
        self.assertEqual(items[0]["fr"], "maison")
        self.assertEqual(items[0]["fr_info"], "{f}")
        self.assertEqual(items[0]["german"], "Haus")
        self.assertEqual(items[0]["german_info"], "{n} [Gebäude]")
        self.assertEqual(items[0]["votes"], 542)

    def test_spanish_pair(self):
        items = dom.parse_table(_read("trans-haus-es.html"), "es")
        self.assertEqual(len(items), 15)
        self.assertEqual(items[0]["es"], "casa")
        self.assertEqual(items[0]["german"], "Haus")

    def test_nomatch(self):
        items = dom.parse_table(_read("trans-nomatch.html"), "en")
        self.assertEqual(items, [])
        self.assertEqual(dom.detect_direction(items, "Xyzqweabc", "en"),
                         "unknown")


class TestSearch(unittest.TestCase):
    def test_hau(self):
        hits = dom.parse_search(_read("search-hau.html"), "en", "Hau")
        self.assertEqual(hits, [
            {"word": "Hau", "lang": "de"},
            {"word": "Hau-den-Lukas", "lang": "de"},
            {"word": "Hau-den-Maulwurf", "lang": "de"}])

    def test_haus(self):
        hits = dom.parse_search(_read("trans-haus.html"), "en", "Haus")
        self.assertEqual(hits[0], {"word": "Haus-", "lang": "de"})
        self.assertIn({"word": "Haus", "lang": "de"}, hits)
        # translations must not leak in as headwords
        self.assertNotIn({"word": "domestic", "lang": "en"}, hits)


class TestServerWiring(unittest.TestCase):
    def test_translate_uses_fixture(self):
        html = _read("trans-haus.html")
        with mock.patch("dictcc_mcp.server._http.fetch_text",
                        return_value=html):
            out = json.loads(srv.dictcc_translate("Haus", limit=3))
        self.assertEqual(out["source"], "dict.cc")
        self.assertEqual(out["total_results"], 50)
        self.assertEqual(out["count"], 3)
        self.assertEqual(out["direction"], "de -> en")
        self.assertEqual(out["items"][0]["en"], "domestic")

    def test_translate_empty(self):
        html = _read("trans-nomatch.html")
        with mock.patch("dictcc_mcp.server._http.fetch_text",
                        return_value=html):
            out = json.loads(srv.dictcc_translate("Xyzqweabc"))
        self.assertEqual(out["total_results"], 0)
        self.assertEqual(out["items"], [])
        self.assertEqual(out["direction"], "unknown")
        self.assertNotIn("error", out)

    def test_invalid_pair(self):
        out = json.loads(srv.dictcc_translate("Haus", pair="en-de"))
        self.assertIn("error", out)


if __name__ == "__main__":
    unittest.main()
