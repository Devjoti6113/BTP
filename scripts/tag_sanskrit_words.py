#!/usr/bin/env python3
"""
tag_sanskrit_words.py
=====================
Reads English transcripts from the Prabhupadavani / CMST dataset (TSV format),
detects Sanskrit words and multi-word expressions using a curated dictionary,
and wraps them in <s>...</s> tags.

Usage
-----
    python scripts/tag_sanskrit_words.py \
        --input  data/raw/sample/sample_transcripts.tsv \
        --output data/processed/sample/sample_tagged.tsv

    # Process all splits
    for split in train dev test; do
        python scripts/tag_sanskrit_words.py \\
            --input  data/raw/${split}.tsv \\
            --output data/processed/${split}_tagged.tsv
    done

Input format
------------
A tab-separated file with at least the columns:
    time_stamp  <TAB>  english

Output format
-------------
Same file with an extra column:
    english_tagged

where Sanskrit spans are enclosed in <s>...</s> tags.
"""

import argparse
import csv
import os
import re
import sys


# ---------------------------------------------------------------------------
# Sanskrit vocabulary
# ---------------------------------------------------------------------------
# Multi-word expressions are listed first so they are matched before their
# individual words.  All entries are stored in lower-case; matching is
# case-insensitive.

SANSKRIT_MULTIWORD = [
    # Bhagavad-gita shlokas / verses (transliterated)
    "aham sarvasya prabhavo mattah sarvam pravartate",
    "sarvasya caham hrdi sannivisto",
    "sarva-dharman parityajya mam ekam saranam vraja",
    "aham evasam evagre",
    "om namo bhagavate vasudevaya",
    # Compound terms
    "bhakti yoga",
    "jnana yoga",
    "karma yoga",
    "raja yoga",
    "hatha yoga",
    "ananya bhakti",
    "uttama bhakti",
    "dharma sanrakshana",
    "nirguna brahman",
    "saguna brahman",
    "para brahman",
    "param dhama",
    "param brahma",
    "sat cit ananda",
    "sac cid ananda",
    "sri krishna",
    "lord krishna",
    "sri rama",
    "sri vishnu",
    "sri narayana",
    "sri caitanya",
    "bhagavad gita",
    "bhagavad-gita",
    "srimad bhagavatam",
    "srimad-bhagavatam",
    "hari nama",
    "hare krishna",
    "hare rama",
    "prana pratistha",
    "guru parampara",
    "sampradaya parampara",
]

SANSKRIT_SINGLE = [
    # Philosophical / theological terms
    "dharma",
    "adharma",
    "karma",
    "akarma",
    "vikarma",
    "yoga",
    "jnana",
    "bhakti",
    "moksha",
    "mukti",
    "samsara",
    "nirvana",
    "brahman",
    "atma",
    "anatma",
    "paramatma",
    "jivatma",
    "maya",
    "avidya",
    "prakriti",
    "purusha",
    "gunas",
    "guna",
    "sattva",
    "rajas",
    "tamas",
    "tapas",
    "tapasya",
    "ahimsa",
    "satya",
    "asteya",
    "aparigraha",
    "brahmacharya",
    "santosha",
    "svadhyaya",
    "ishvara",
    "pranidhana",
    "samadhi",
    "dharana",
    "dhyana",
    "pratyahara",
    "pranayama",
    "asana",
    "yama",
    "niyama",
    "vairagya",
    "viveka",
    "mumukshu",
    "sadhaka",
    "sadhana",
    "siddhi",
    "samskara",
    "vasana",
    "chitta",
    "manas",
    "buddhi",
    "ahamkara",
    "antahkarana",
    "prana",
    "apana",
    "vyana",
    "udana",
    "samana",
    "kosha",
    "annamaya",
    "pranamaya",
    "manomaya",
    "vijnanamaya",
    "anandamaya",
    # Deities and sacred names
    "krishna",
    "vishnu",
    "shiva",
    "brahma",
    "narayana",
    "rama",
    "radha",
    "lakshmi",
    "saraswati",
    "durga",
    "kali",
    "ganesha",
    "hanuman",
    "arjuna",
    "yudhishthira",
    "bhima",
    "nakula",
    "sahadeva",
    "draupadi",
    "kunti",
    "duryodhana",
    "bhishma",
    "drona",
    "karna",
    "vasudeva",
    "devaki",
    "nanda",
    "yashoda",
    "balaram",
    "subhadra",
    "prabhupada",
    "caitanya",
    "mahaprabhu",
    "nityananda",
    "advaita",
    "gadadhara",
    "srivasa",
    # Scriptural / textual terms
    "veda",
    "vedas",
    "vedanta",
    "upanishad",
    "upanishads",
    "puranas",
    "purana",
    "bhagavatam",
    "mahabharata",
    "ramayana",
    "gita",
    "shastra",
    "shastras",
    "sruti",
    "smriti",
    "itihasa",
    "sutra",
    "sutras",
    "mantra",
    "mantras",
    "stotra",
    "stotras",
    "sloka",
    "shloka",
    "slokas",
    "shlokas",
    "tantra",
    # Practices / places / communities
    "ashram",
    "ashrama",
    "gurukula",
    "guru",
    "shishya",
    "sampradaya",
    "parampara",
    "satsang",
    "satsanga",
    "kirtana",
    "kirtan",
    "bhajan",
    "puja",
    "pooja",
    "arati",
    "aarti",
    "yajna",
    "yagna",
    "homa",
    "prasad",
    "prasada",
    "tirtha",
    "dham",
    "dhamah",
    "vrindavan",
    "vrindavana",
    "mathura",
    "dvarka",
    "dwaraka",
    "ayodhya",
    "kurukshetra",
    "kashi",
    "varanasi",
    "haridwar",
    "rishikesh",
    # Miscellaneous Sanskrit terms common in Prabhupada's lectures
    "lila",
    "lilas",
    "rasa",
    "rasas",
    "svarupa",
    "vaikuntha",
    "goloka",
    "vraja",
    "gokula",
    "nitya",
    "seva",
    "sevaka",
    "sevya",
    "bhava",
    "prema",
    "sneha",
    "vatsalya",
    "sakhya",
    "dasya",
    "madhurya",
    "shanta",
    "aishvarya",
    "sat",
    "chit",
    "ananda",
    "sukha",
    "dukha",
    "kama",
    "lobha",
    "moha",
    "mada",
    "matsarya",
    "krodha",
    "jiva",
    "jivas",
    "kshetra",
    "kshetrajna",
    "avyakta",
    "vyakta",
    "akshara",
    "kshara",
    "uttama",
    "purushottama",
    "maha",
    "mahabhava",
    "acharya",
    "swami",
    "sadhu",
    "sant",
    "bhakta",
    "bhaktas",
    "vaishnava",
    "vaishnavas",
    "shaivite",
    "smartha",
]

# Build a single sorted list: multi-word first (longest first), then single
ALL_TERMS = sorted(SANSKRIT_MULTIWORD, key=len, reverse=True) + \
            sorted(SANSKRIT_SINGLE, key=len, reverse=True)

# Pre-compile a single alternation regex for efficiency.
# Wrap each term in a word-boundary assertion so we don't match sub-strings.
def _build_pattern(terms):
    escaped = [re.escape(t) for t in terms]
    # \b works for ASCII word boundaries; use lookahead/lookbehind for hyphens
    pattern = r"(?<!['\-\w])(" + "|".join(escaped) + r")(?!['\-\w])"
    return re.compile(pattern, re.IGNORECASE)


SANSKRIT_RE = _build_pattern(ALL_TERMS)


# ---------------------------------------------------------------------------
# Core tagging logic
# ---------------------------------------------------------------------------

def tag_sanskrit(text: str) -> str:
    """
    Wrap every Sanskrit word / expression found in *text* with <s>...</s> tags.

    The function preserves original casing inside the tags.  Overlapping or
    adjacent matches are merged into a single tag.

    Parameters
    ----------
    text : str
        Raw English transcript (may contain Sanskrit words).

    Returns
    -------
    str
        Transcript with Sanskrit spans enclosed in ``<s>…</s>``.
    """
    if not text or not text.strip():
        return text

    # Collect all match spans
    spans = [(m.start(), m.end()) for m in SANSKRIT_RE.finditer(text)]

    if not spans:
        return text

    # Merge overlapping / adjacent spans
    merged = []
    current_start, current_end = spans[0]
    for start, end in spans[1:]:
        if start <= current_end + 1:          # overlapping or touching
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end
    merged.append((current_start, current_end))

    # Reconstruct the string with tags inserted
    result = []
    prev = 0
    for start, end in merged:
        result.append(text[prev:start])
        result.append("<s>")
        result.append(text[start:end])
        result.append("</s>")
        prev = end
    result.append(text[prev:])
    return "".join(result)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def process_file(input_path: str, output_path: str,
                 text_col: str = "english",
                 tagged_col: str = "english_tagged") -> int:
    """
    Read a TSV file, tag Sanskrit words in *text_col*, write result to
    *output_path* with an additional *tagged_col* column.

    Returns the number of rows processed.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    rows_processed = 0

    with open(input_path, newline="", encoding="utf-8") as fin, \
         open(output_path, "w", newline="", encoding="utf-8") as fout:

        reader = csv.DictReader(fin, delimiter="\t")
        if reader.fieldnames is None:
            print(f"[ERROR] Could not read header from {input_path}", file=sys.stderr)
            return 0

        if text_col not in reader.fieldnames:
            print(
                f"[ERROR] Column '{text_col}' not found in {input_path}. "
                f"Available columns: {reader.fieldnames}",
                file=sys.stderr,
            )
            return 0

        fieldnames = list(reader.fieldnames) + [tagged_col]
        writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter="\t",
                                extrasaction="ignore")
        writer.writeheader()

        for row in reader:
            row[tagged_col] = tag_sanskrit(row.get(text_col, ""))
            writer.writerow(row)
            rows_processed += 1

    return rows_processed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Tag Sanskrit words in English Prabhupadavani transcripts "
                    "with <s>...</s> markers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to the input TSV file (must contain a header row).",
    )
    parser.add_argument(
        "--output", "-o", required=True,
        help="Path for the output TSV file (created if it does not exist).",
    )
    parser.add_argument(
        "--text-col", default="english",
        help="Name of the column containing the English transcript "
             "(default: 'english').",
    )
    parser.add_argument(
        "--tagged-col", default="english_tagged",
        help="Name of the output column for tagged text "
             "(default: 'english_tagged').",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(f"Processing: {args.input} → {args.output}")
    n = process_file(
        args.input, args.output,
        text_col=args.text_col,
        tagged_col=args.tagged_col,
    )
    if n > 0:
        print(f"Done. {n} rows written to {args.output}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
