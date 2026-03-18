#!/usr/bin/env python3
"""
tests/test_tag_sanskrit_words.py
================================
Unit tests for the Sanskrit tagging script.
Run with:  python -m pytest tests/ -v
"""

import csv
import io
import os
import sys
import tempfile

# Allow importing from the scripts directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from tag_sanskrit_words import tag_sanskrit, process_file  # noqa: E402


# ---------------------------------------------------------------------------
# tag_sanskrit() unit tests
# ---------------------------------------------------------------------------

class TestTagSanskrit:

    def test_no_sanskrit(self):
        text = "The quick brown fox jumps over the lazy dog."
        assert tag_sanskrit(text) == text

    def test_single_word(self):
        result = tag_sanskrit("He practices yoga every morning.")
        assert result == "He practices <s>yoga</s> every morning."

    def test_case_insensitive(self):
        # Original casing must be preserved inside the tag
        result = tag_sanskrit("He practices Yoga every morning.")
        assert result == "He practices <s>Yoga</s> every morning."

    def test_multiword_expression(self):
        result = tag_sanskrit("This is the path of bhakti yoga.")
        assert "<s>bhakti yoga</s>" in result

    def test_multiword_takes_priority_over_single(self):
        # "bhakti yoga" should be a single span, not two separate spans
        result = tag_sanskrit("Follow the path of bhakti yoga always.")
        assert "<s>bhakti yoga</s>" in result
        # Ensure there is NOT a separate <s>bhakti</s> or <s>yoga</s>
        assert result.count("<s>") == 1

    def test_multiple_words_in_sentence(self):
        result = tag_sanskrit(
            "Krishna teaches dharma and karma to Arjuna."
        )
        assert "<s>Krishna</s>" in result
        assert "<s>dharma</s>" in result
        assert "<s>karma</s>" in result
        assert "<s>Arjuna</s>" in result

    def test_long_shloka(self):
        text = (
            "This is the final teaching: "
            "sarva-dharman parityajya mam ekam saranam vraja."
        )
        result = tag_sanskrit(text)
        assert "<s>sarva-dharman parityajya mam ekam saranam vraja</s>" in result

    def test_empty_string(self):
        assert tag_sanskrit("") == ""

    def test_whitespace_only(self):
        assert tag_sanskrit("   ") == "   "

    def test_vedic_verse_multiword(self):
        text = "Om namo bhagavate vasudevaya is a Vaishnava mantra."
        result = tag_sanskrit(text)
        assert "<s>Om namo bhagavate vasudevaya</s>" in result

    def test_word_boundary(self):
        # "yoga" should not match inside "Mythology"
        text = "Greek Mythology is interesting."
        assert tag_sanskrit(text) == text


# ---------------------------------------------------------------------------
# process_file() integration tests
# ---------------------------------------------------------------------------

class TestProcessFile:

    def _make_tsv(self, rows, fieldnames=("time_stamp", "english")):
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return buf.getvalue()

    def test_basic_round_trip(self):
        content = self._make_tsv([
            {"time_stamp": "BG_4_8",
             "english": "Reestablish the principles of dharma."},
        ])
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv",
                                         delete=False, encoding="utf-8") as fin:
            fin.write(content)
            in_path = fin.name

        out_path = in_path + "_out.tsv"
        try:
            n = process_file(in_path, out_path)
            assert n == 1
            with open(out_path, encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t")
                rows = list(reader)
            assert len(rows) == 1
            assert "<s>dharma</s>" in rows[0]["english_tagged"]
        finally:
            os.unlink(in_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_missing_column_returns_zero(self):
        content = self._make_tsv(
            [{"time_stamp": "X1", "english": "Some text."}],
            fieldnames=("time_stamp", "english"),
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv",
                                         delete=False, encoding="utf-8") as fin:
            fin.write(content)
            in_path = fin.name

        out_path = in_path + "_out.tsv"
        try:
            n = process_file(in_path, out_path, text_col="nonexistent_col")
            assert n == 0
        finally:
            os.unlink(in_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_sample_file(self):
        """Integration test using the checked-in sample file."""
        repo_root = os.path.join(os.path.dirname(__file__), "..")
        in_path = os.path.join(repo_root, "data", "raw", "sample",
                               "sample_transcripts.tsv")
        if not os.path.exists(in_path):
            return  # skip if sample file not present

        with tempfile.NamedTemporaryFile(suffix=".tsv", delete=False) as tmp:
            out_path = tmp.name

        try:
            n = process_file(in_path, out_path)
            assert n > 0
            with open(out_path, encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t")
                rows = list(reader)
            # At least one row should have a Sanskrit tag
            tagged = [r for r in rows if "<s>" in r.get("english_tagged", "")]
            assert len(tagged) > 0
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)
