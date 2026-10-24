# Publishing to Kaggle — One-Time Setup

The GitHub Action in this repo can publish every merged weekly file to
Kaggle automatically. It needs three one-time steps. Nothing in this
repo contains a Kaggle key, and no key should ever be committed.

## Step 1 — Connect / sign in to Kaggle

1. Sign in at https://www.kaggle.com/ in the browser.
2. Note your exact Kaggle username — it is in your profile URL:
   `https://www.kaggle.com/<KAGGLE_USERNAME>`
3. *Optional, if Kaggle shows it:* Kaggle → Settings → Account may offer
   a GitHub connection under connected accounts. Linking it connects your
   Kaggle identity to GitHub for sign-in / profile purposes. It does **not**
   give GitHub Actions permission to publish datasets — that is Step 2.
   Dataset publishing always uses the Kaggle API token below.

## Step 2 — Create a Kaggle API token and add it to GitHub Secrets

1. Kaggle → Settings → API → **Create New Token**.
   This downloads a `kaggle.json` file containing `username` and `key`.
   Treat it like a password. Do not commit it, paste it in chat, or put
   it in this repo.
2. In this GitHub repo: Settings → Secrets and variables → Actions →
   New repository secret. Add exactly:
   - `KAGGLE_USERNAME` — the `username` value from `kaggle.json`
   - `KAGGLE_KEY` — the `key` value from `kaggle.json`
3. Delete the downloaded `kaggle.json` or keep it outside the repo.

## Step 3 — Dataset slug (already set)

Verified 2026-10-23: Kaggle username is `saivanka`
(profile: https://www.kaggle.com/saivanka), the same as the GitHub username.

`kaggle/dataset-metadata.json` is already set to:

```
saivanka/us-retail-gasoline-and-diesel-prices-weekly
```

No change is needed unless the Kaggle username ever changes.

## How publishing works after setup

- Merging a PR that changes `data/**` into `main` triggers
  `.github/workflows/publish-to-kaggle.yml`.
- You can also run it manually: GitHub → Actions →
  “Publish to Kaggle” → Run workflow.
- The workflow:
  1. Validates every CSV in `data/incoming/` (`scripts/validate_csv.py`).
  2. Stages a clean upload folder with the CSVs + `dataset-metadata.json`.
  3. Runs `scripts/publish_to_kaggle.py`, which creates the dataset on
     first run, and creates a new dataset version on every later run.
- If the secrets are missing, the workflow fails at the credentials step
  with a clear message — it never publishes a partial or invalid file.

## First run checklist

- [x] Signed in to Kaggle, username confirmed (`saivanka`, verified 2026-10-23)
- [ ] `KAGGLE_USERNAME` and `KAGGLE_KEY` secrets added to this repo
- [x] Dataset id set to `saivanka/us-retail-gasoline-and-diesel-prices-weekly` in `kaggle/dataset-metadata.json`
- [ ] Workflow run manually once from the Actions tab
- [ ] Dataset appears at
      `https://www.kaggle.com/datasets/saivanka/us-retail-gasoline-and-diesel-prices-weekly`
- [ ] README Kaggle link updated with the real username

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `Kaggle credentials not found` | Secrets missing or named differently — they must be exactly `KAGGLE_USERNAME` / `KAGGLE_KEY`. |
| `403 Forbidden` from Kaggle API | Token revoked or account not verified on Kaggle — create a new token in Step 2. |
| Validation fails in Actions | The CSV broke a rule in `docs/METHODOLOGY.md` — fix the file, never weaken the validator to publish. |
| Dataset created but empty | The staging step found no CSVs — check files are under `data/incoming/` and end in `.csv`. |
