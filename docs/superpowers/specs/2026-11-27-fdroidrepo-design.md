# F-Droid repository migration

## Intent and scope

Publish the signed F-Droid repository at
`https://panlelapin.github.io/fdroidrepo/`, backed by
`https://github.com/panlelapin/fdroidrepo`.
The user approved this scope, including publication on GitHub.

Move the public contents of `fdroid/repo/` to the repository root.
Rename `catalogue/` to `catalog/`. Use professional English in documentation,
workflow labels, script messages, and app and repository descriptions.
Keep the Pan le lapin brand, application identifiers, APKs, and signing keys.

## Approaches

- Keep the current GitHub name and flatten only the Pages artifact: simpler,
  but does not provide the requested `/fdroidrepo/` address.
- Rename the GitHub repository and flatten both the tracked public files and
  Pages artifact: the approved approach; source layout matches the public URL.

## Constraints and implementation choices

Regenerate signed indexes and the QR code through GitHub Actions, where the
existing index signing secrets are available. Never edit signed indexes by
hand or expose signing material. Publish only public repository assets, not
the development files under `catalog/`, `.github/`, or `docs/`.

Update references to the reusable APK signing workflow in the application
repositories if needed, preserving commit pins and unrelated content.
The old GitHub Pages address is not guaranteed to redirect; existing users
may need to add the new repository address. Providing a legacy site or
renaming the local workspace is out of scope.

The user subsequently requested working directly in the existing checkout and
renaming the local and remote default branch from `main` to `master`.

The first publication exposed fdroidserver 2.4.5's `/repo` configuration
restriction. Load a conventional staging URL, then set the actual public URL
in the initialized fdroidserver configuration before generation. This
compatibility adapter must not rewrite generated or signed metadata.

## Verification

Test import rules, root-layout staging, address migration without a new APK,
and public artifact isolation. Run the publishing workflow, verify the
unchanged signing certificate, and inspect the live root index, QR link,
English descriptions, and APK links.
