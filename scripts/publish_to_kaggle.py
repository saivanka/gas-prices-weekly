#!/usr/bin/env python3
"""Publish data/incoming/*.csv to Kaggle as one dataset.

Requires the `kaggle` CLI (pip install kaggle) and credentials in the
environment. Two credential forms are accepted:
- Legacy: KAGGLE_USERNAME + KAGGLE_KEY (from kaggle.json), or
- New-style API token: KAGGLE_API_TOKEN (the workflow maps the token
  stored in the KAGGLE_KEY secret to this variable — the current Kaggle
  CLI authenticates new-style tokens only this way).
See docs/KAGGLE_SETUP.md.

Creates the dataset on first run; creates a new version after that.
The metadata template in kaggle/dataset-metadata.json must have its
YOUR_KAGGLE_USERNAME placeholder replaced before the first run.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "kaggle_upload"


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> int:
    template = (ROOT / "kaggle" / "dataset-metadata.json").read_text(encoding="utf-8")
    if "YOUR_KAGGLE_USERNAME" in template:
        print("ERROR: replace YOUR_KAGGLE_USERNAME in kaggle/dataset-metadata.json first.")
        return 1

    username = os.environ.get("KAGGLE_USERNAME", "").strip()
    if not username:
        # Fall back to the owner already set in the metadata id.
        username = json.loads(template)["id"].split("/", 1)[0]
    has_legacy = bool(username and os.environ.get("KAGGLE_KEY", "").strip())
    has_token = bool(os.environ.get("KAGGLE_API_TOKEN", "").strip())
    if not (has_legacy or has_token):
        print("ERROR: no Kaggle credentials in the environment. Set the "
              "KAGGLE_USERNAME / KAGGLE_KEY repository secrets (the workflow "
              "maps KAGGLE_KEY to KAGGLE_API_TOKEN for new-style tokens) — "
              "see docs/KAGGLE_SETUP.md")
        return 1

    metadata = json.loads(template.replace("<KAGGLE_USERNAME>", username))
    metadata["id"] = f"{username}/{metadata['id'].split('/', 1)[-1]}"

    csvs = sorted((ROOT / "data" / "incoming").glob("*.csv"))
    if not csvs:
        print("ERROR: no CSV files under data/incoming/")
        return 1

    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    for csv_file in csvs:
        shutil.copy2(csv_file, STAGE / csv_file.name)
    (STAGE / "dataset-metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Staged {len(csvs)} CSV(s) for dataset {metadata['id']}")

    # Try a new version first (dataset exists); fall back to create.
    version = run(["kaggle", "datasets", "version", "-p", str(STAGE),
                   "-m", f"Weekly update {csvs[-1].stem}", "--dir-mode", "zip"])
    print(version.stdout.strip())
    if version.returncode == 0:
        print(f"Published new version of {metadata['id']}")
        return 0
    print(version.stderr.strip())
    print("Version failed — attempting initial dataset creation...")
    create = run(["kaggle", "datasets", "create", "-p", str(STAGE)])
    print(create.stdout.strip())
    print(create.stderr.strip())
    if create.returncode == 0:
        print(f"Created dataset {metadata['id']}")
        return 0
    print("ERROR: Kaggle publish failed (both version and create).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
