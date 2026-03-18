# Processed Data — Sanskrit-Tagged Transcripts

This folder stores English transcripts **after** Sanskrit words and phrases have
been wrapped in `<s>...</s>` tags.

## Tag convention

| Tag    | Meaning                                               |
|--------|-------------------------------------------------------|
| `<s>`  | Opening tag — marks the start of a Sanskrit span      |
| `</s>` | Closing tag — marks the end of a Sanskrit span        |

### Example

**Input (raw):**
```
To deliver the pious and to annihilate the miscreants, as well as to reestablish
the principles of dharma, I Myself appear, millennium after millennium.
```

**Output (tagged):**
```
To deliver the pious and to annihilate the miscreants, as well as to reestablish
the principles of <s>dharma</s>, I Myself appear, millennium after millennium.
```

Multi-word Sanskrit expressions are enclosed in a single tag pair:

```
This is the final instruction of the Bhagavad-gita,
<s>sarva-dharman parityajya mam ekam saranam vraja</s>.
```

## File format

Files mirror the raw TSV format with an additional `english_tagged` column:

| Column           | Description                                              |
|------------------|----------------------------------------------------------|
| `time_stamp`     | Audio clip name / ID (same as raw)                       |
| `english`        | Original English transcript (unchanged)                  |
| `english_tagged` | Transcript with Sanskrit spans wrapped in `<s>...</s>`  |

## How to generate

Run the tagging script from the repository root:

```bash
python scripts/tag_sanskrit_words.py \
    --input  data/raw/sample/sample_transcripts.tsv \
    --output data/processed/sample/sample_tagged.tsv
```

To process all splits at once:

```bash
for split in train dev test; do
    python scripts/tag_sanskrit_words.py \
        --input  data/raw/${split}.tsv \
        --output data/processed/${split}_tagged.tsv
done
```

## Sample data

See `sample/sample_tagged.tsv` for a small illustrative extract produced from
`data/raw/sample/sample_transcripts.tsv`.
