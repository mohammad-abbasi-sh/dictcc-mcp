"""Live tests — hit the real dict.cc search pages. Cautious: few requests.

Run:  pytest tests/test_live.py -v
Skip: pytest -m "not live"  (or set DICTCC_SKIP_LIVE=1)
"""
import json
import os
import pathlib
import sys
import unittest

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from dictcc_mcp import server as srv

pytestmark = pytest.mark.live
SKIP = os.environ.get("DICTCC_SKIP_LIVE") == "1"


@pytest.mark.skipif(SKIP, reason="DICTCC_SKIP_LIVE=1")
class TestLive(unittest.TestCase):
    def test_translate_live(self):
        out = json.loads(srv.dictcc_translate("Haus", limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 10)
        self.assertEqual(out["direction"], "de -> en")
        print(f"\nLIVE translate Haus: {out['total_results']} rows — "
              f"top: {out['items'][0]['en']}")

    def test_translate_english_live(self):
        out = json.loads(srv.dictcc_translate("house", limit=3))
        self.assertNotIn("error", out)
        self.assertEqual(out["direction"], "en -> de")

    def test_translate_french_live(self):
        out = json.loads(srv.dictcc_translate("Haus", pair="de-fr", limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 5)
        self.assertEqual(out["items"][0]["fr"], "maison")

    def test_search_live(self):
        out = json.loads(srv.dictcc_search("Haus", limit=5))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 1)
        self.assertEqual(out["items"][0]["word"], "Haus-")

    def test_nomatch_live(self):
        out = json.loads(srv.dictcc_translate("Xyzqweabc"))
        self.assertNotIn("error", out)
        self.assertEqual(out["total_results"], 0)
