# BTP — Sanskrit / English Code-Switching ASR

This repository contains the data pipeline and processing scripts for a
**real-time subtitle generation system** that handles code-switching between
English and Sanskrit in Prabhupada's (Prabhupadavani) audio lectures.

---

## Goal

When Prabhupada speaks he naturally switches between English and Sanskrit
(quoting Vedic verses, using Sanskrit terminology, etc.).  The aim of this
project is to:

1. Obtain the English audio transcripts from the
   [Prabhupadavani / CMST dataset](https://github.com/frozentoad9/CMST).
2. Mark all Sanskrit words and expressions in those transcripts with
   `<s>…</s>` tags so that a downstream ASR model can switch its decoding
   language model at those points.
3. Use the tagged transcripts as training / evaluation data for a
   code-switching ASR pipeline.

---

## Repository layout

```
BTP/
├── data/
│   ├── raw/                  ← Source English transcripts (CMST / Google Drive)
│   │   ├── README.md         ← How to download the source data
│   │   └── sample/
│   │       └── sample_transcripts.tsv
│   └── processed/            ← Tagged output (<s>…</s> around Sanskrit spans)
│       ├── README.md
│       └── sample/
│           └── sample_tagged.tsv
├── scripts/
│   ├── tag_sanskrit_words.py     ← Main tagging script
│   └── download_cmst_data.py     ← Helper to fetch data from Google Drive
├── tests/
│   └── test_tag_sanskrit_words.py
├── requirements.txt
└── README.md
```

---

## Quick start

### 1 — Download the source data

```bash
pip install -r requirements.txt
python scripts/download_cmst_data.py --translations-only
```

This downloads the train / dev / test CSV/TSV splits from the Prabhupadavani
Google Drive into `data/raw/`.  See `data/raw/README.md` for manual download
instructions.

### 2 — Tag Sanskrit words

```bash
python scripts/tag_sanskrit_words.py \
    --input  data/raw/train.tsv \
    --output data/processed/train_tagged.tsv
```

Repeat for `dev.tsv` and `test.tsv`.  The script adds an `english_tagged`
column where every Sanskrit word / phrase is wrapped in `<s>…</s>`.

**Example output:**

| time\_stamp | english | english\_tagged |
|-------------|---------|-----------------|
| BG\_4\_8 | … reestablish the principles of dharma … | … reestablish the principles of `<s>dharma</s>` … |
| BG\_18\_66 | … sarva-dharman parityajya mam ekam saranam vraja | … `<s>sarva-dharman parityajya mam ekam saranam vraja</s>` |

### 3 — Run the tests

```bash
python -m pytest tests/ -v
```

---

## Source dataset

**Prabhupadavani / CMST** (Code-Mixed Speech Translation):
- Paper: [COLING 2022, SIGHUM workshop](https://aclanthology.org/2022.latechclfl-1.4/)
- GitHub: https://github.com/frozentoad9/CMST
- Licence: Apache 2.0

The dataset contains 94 hours of Prabhupada's speech aligned with manual
translations in 25 languages.  The English transcripts exhibit code-switching
between English and Sanskrit.

---

## Citation

If you use the Prabhupadavani dataset please cite:

```bibtex
@inproceedings{sandhan-etal-2022-prabhupadavani,
    title = "Prabhupadavani: A Code-mixed Speech Translation Data for 25 Languages",
    author = "Sandhan, Jivnesh and Daksh, Ayush and Paranjay, Om Adideva
              and Behera, Laxmidhar and Goyal, Pawan",
    booktitle = "Proceedings of the 6th Joint SIGHUM Workshop on Computational
                 Linguistics for Cultural Heritage, Social Sciences, Humanities
                 and Literature",
    month = oct,
    year = "2022",
    url = "https://aclanthology.org/2022.latechclfl-1.4",
    pages = "24--29",
}
```
