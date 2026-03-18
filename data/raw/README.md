# Raw Data — Source Transcripts (CMST / Prabhupadavani)

This folder stores the **unmodified** English audio transcripts sourced from the
[Prabhupadavani / CMST dataset](https://github.com/frozentoad9/CMST).

## About the source dataset

*Prabhupadavani* is a multilingual code-mixed speech-translation dataset published
at COLING 2022 (SIGHUM workshop).  It contains 94 hours of speech by Srila
Prabhupada aligned with manual translations in 25 languages.  The English
transcripts contain **code-switching** between English and Sanskrit: whenever
Prabhupada quotes from Vedic literature he naturally switches to Sanskrit
(intra-sentential or inter-sentential switching).

Paper: https://aclanthology.org/2022.latechclfl-1.4/

## How to download the source data

The data is hosted on Google Drive and distributed under the Apache 2.0 licence.

1. **Translations only (train / dev / test splits)**
   https://drive.google.com/drive/folders/1mnCjP4woF0CrQfhXajj90xp13TW-moR1

2. **Audio + transcription + translation (full)**
   https://drive.google.com/drive/folders/1F_TM0EwlZG36ZbbqgzWdWagxsYR70cuN

After downloading, place the CSV/TSV files under this folder keeping the original
split structure, e.g.:

```
data/raw/
├── train.tsv
├── dev.tsv
└── test.tsv
```

The script `scripts/download_cmst_data.py` can automate this step if you have a
`gdown`-compatible share link.

## File format

Each file is a **tab-separated** table with at minimum the following columns:

| Column       | Description                                        |
|--------------|----------------------------------------------------|
| `time_stamp` | Name / ID of the corresponding audio clip          |
| `english`    | English transcript (may contain Sanskrit passages) |

Additional columns hold translations in other languages and are not used by this
pipeline.

## Sample data

See `sample/sample_transcripts.tsv` for a small illustrative extract.
