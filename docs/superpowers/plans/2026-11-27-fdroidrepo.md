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

- [x] Inspect both application release workflows for reusable workflow references.
- [x] Rename `panlelapin/android` to `panlelapin/fdroidrepo` with GitHub CLI and
  update `origin` to `https://github.com/panlelapin/fdroidrepo.git`.
- [x] Rename remote `main` to `master`, verify the default branch, and rename
  the local branch and tracking configuration.
- [x] Update caller repository paths if required, keeping their pinned revisions.
- [x] Push the migration and dispatch `catalog.yml`.
- [x] Wait for the signing and Pages jobs; inspect logs and resolve failures
  before claiming publication succeeded.
- [x] Verify live `index-v2.json` and `entry.jar`, unchanged certificate fingerprint,
  new root URL, English descriptions, QR target, and downloadable APK hashes.
- [x] Synchronize generated public assets locally; record verification and mark
  these checkboxes complete.

## Delivery verification

- [Publication run 46008120482](https://github.com/panlelapin/fdroidrepo/actions/runs/46008120482):
  signing/index job and Pages job succeeded.
- Eight tests pass with fdroidserver 2.4.5 installed, including real unsigned
  index generation using the custom root URL.
- Independent code review found no critical, important, or minor issues before
  publication. Integration failures subsequently received RED-to-GREEN tests.
- OpenSSL verified the live entry JAR signature and the unchanged pinned
  certificate; its manifest and signed index digest match the deployed index.
- All four published APK hashes match both the signed index and local files.
- App icons are available with correct hashes. The generated landing page and
  QR code resolve to the new root URL with the original signing fingerprint.
- Development paths `catalog/apps.json`, `README.md`, and
  `.github/workflows/catalog.yml` return HTTP 404 on Pages.
- The default branch and Pages source are `master`; the remote exposes only
  `master`, and local tracking and `origin/HEAD` point to it.

## Implementation decisions and risks

- Work directly in the checkout and rename `main` to `master`, as explicitly
  requested. All active branch references were updated; a missed reference
  would prevent the affected workflow from running.
- Use one public-asset allowlist for signing staging and deployment rather
  than publishing the entire root. An omitted asset would be unavailable;
  regression tests and live checks cover the current assets.
- Merge two previously unpulled automated updates, preserving both newer APKs
  and relocating their assets. Incorrect relocation could hide an app version;
  all four versions were verified live.
- Load a conventional staging URL, then set fdroidserver's public URL in
  memory before generation. This avoids modifying signed files. Upstream API
  changes could break the adapter; the dependency is pinned and a real
  index-generation test runs in CI.

No review findings were deferred.
