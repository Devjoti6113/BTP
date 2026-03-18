#!/usr/bin/env python3
"""
download_cmst_data.py
=====================
Helper script to download the Prabhupadavani / CMST dataset from Google Drive
and place the files in the expected locations under data/raw/.

Requires ``gdown`` (pip install gdown).

Google Drive folder IDs
-----------------------
* Translations only (train/dev/test splits):
  1mnCjP4woF0CrQfhXajj90xp13TW-moR1

* Full dataset (audio + transcription + translation):
  1F_TM0EwlZG36ZbbqgzWdWagxsYR70cuN

Usage
-----
    # Download translations (CSV/TSV splits) only
    python scripts/download_cmst_data.py --translations-only

    # Download full dataset (audio + text)
    python scripts/download_cmst_data.py --full

    # Specify a custom output directory
    python scripts/download_cmst_data.py --translations-only --output-dir data/raw
"""

import argparse
import os
import sys


# Google Drive folder identifiers as listed in the CMST README
TRANSLATIONS_FOLDER_ID = "1mnCjP4woF0CrQfhXajj90xp13TW-moR1"
FULL_DATASET_FOLDER_ID = "1F_TM0EwlZG36ZbbqgzWdWagxsYR70cuN"


def check_gdown():
    """Verify that gdown is installed."""
    try:
        import gdown  # noqa: F401
    except ImportError:
        print(
            "[ERROR] The 'gdown' package is not installed.\n"
            "Install it with:  pip install gdown",
            file=sys.stderr,
        )
        sys.exit(1)


def download_folder(folder_id: str, output_dir: str):
    """Download a Google Drive folder to *output_dir* using gdown."""
    import gdown

    url = f"https://drive.google.com/drive/folders/{folder_id}"
    print(f"Downloading from: {url}")
    print(f"Destination     : {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    gdown.download_folder(url, output=output_dir, quiet=False, use_cookies=False)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download the Prabhupadavani (CMST) dataset from Google Drive.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--translations-only",
        action="store_true",
        help="Download only the translation CSV/TSV splits (smaller download).",
    )
    group.add_argument(
        "--full",
        action="store_true",
        help="Download the full dataset including audio clips.",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="data/raw",
        help="Directory to save downloaded files (default: data/raw).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    check_gdown()

    if args.translations_only:
        download_folder(TRANSLATIONS_FOLDER_ID, args.output_dir)
    else:
        download_folder(FULL_DATASET_FOLDER_ID, args.output_dir)

    print("\nDownload complete.")
    print(f"Files saved to: {os.path.abspath(args.output_dir)}")
    print(
        "\nNext step — tag Sanskrit words:\n"
        "  python scripts/tag_sanskrit_words.py "
        "--input data/raw/train.tsv --output data/processed/train_tagged.tsv"
    )


if __name__ == "__main__":
    main()
