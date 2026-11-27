# F-Droid Repository Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename and publish the repository at `https://panlelapin.github.io/fdroidrepo/`, with professional English throughout.

**Architecture:** Track public F-Droid files at the root and keep tooling in `catalog/`. Stage only public assets for signing and Pages deployment; regenerate all signed metadata using the existing GitHub Actions secrets.

**Tech Stack:** Python unittest, fdroidserver 2.4.5, GitHub Actions, GitHub Pages, GitHub CLI.

**Spec:** `docs/superpowers/specs/2026-11-27-fdroidrepo-design.md`

## Global Constraints

- Keep application identifiers, APKs, signing keys, and the Pan le lapin brand unchanged.
- Public URL: `https://panlelapin.github.io/fdroidrepo/`.
- Tooling directory: `catalog/`.
- Use professional English for maintained text.
- Never edit signed indexes by hand or expose signing material.
- Preserve unrelated changes and pinned workflow revisions.
- Work directly in the existing checkout; rename the local and remote default branch to `master` (subsequent user instruction).

## Review Focus

- Root staging must exclude source files and secrets.
- Address changes must trigger index regeneration even without new APKs.
- The generated root landing page and QR code must use the new URL.
- Renaming the repository must not break reusable signing workflow callers.
- Published indexes must retain the existing signing certificate and valid APK hashes.

### Task 1: Root layout and English tooling

**Files:** Move `catalogue/` to `catalog/`; move `fdroid/repo/*` to root;
update `catalog/importer.py`, `catalog/sign_index.py`,
`catalog/metadata/com.github.panlelapin.blackbg.yml`, `README.md`,
`.github/workflows/catalogue.yml`, `.github/workflows/sign-apk.yml`.
Replace the old root landing page with the generated repository landing page.
Rename the publishing workflow to `.github/workflows/catalog.yml`.

**Interfaces:** `collect(work, force=False)` stages public files in `work/repo`;
`ADDRESS` defines the canonical URL. The workflow publishes only that public
directory, while committing regenerated assets back to the root.

- [x] Add regression tests for `ADDRESS`, staging the root public assets without
  tooling, and an address-only migration with no new releases.
- [x] Run `python3 -B -m unittest discover -s catalogue -v`; confirm new tests fail.
- [x] Move directories and public assets; introduce a shared public-asset staging
  helper if needed so importer and deployment use the same allowlist.
- [x] Update paths, English descriptions/messages, README, workflow names and
  public artifact assembly. Preserve APK hashes and signature checks.
- [x] Run `python3 -B -m unittest discover -s catalog -v`; confirm all tests pass.
- [x] Review the diff for stale active URLs, French text, and private-file exposure.
- [x] Commit the migration and its regression tests.

### Task 2: GitHub migration and publication

**Files:** Git remote configuration; GitHub repository settings; application
workflow references only where the old repository name is still used.

**Interfaces:** Existing repository secrets remain attached to the renamed
repository; `catalog.yml` signs and deploys the migrated public repository.

- [ ] Inspect both application release workflows for reusable workflow references.
- [ ] Rename `panlelapin/android` to `panlelapin/fdroidrepo` with GitHub CLI and
  update `origin` to `https://github.com/panlelapin/fdroidrepo.git`.
- [ ] Rename remote `main` to `master`, verify the default branch, and rename
  the local branch and tracking configuration.
- [ ] Update caller repository paths if required, keeping their pinned revisions.
- [ ] Push the migration and dispatch `catalog.yml`.
- [ ] Wait for the signing and Pages jobs; inspect logs and resolve failures
  before claiming publication succeeded.
- [ ] Verify live `index-v2.json` and `entry.jar`, unchanged certificate fingerprint,
  new root URL, English descriptions, QR target, and downloadable APK hashes.
- [ ] Synchronize generated public assets locally; record verification and mark
  these checkboxes complete.
