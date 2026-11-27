# Pan le lapin — Android apps

**Pan le lapin** is an F-Droid repository distributing signed Android APKs for BlackBG and WFQA.

## Add the repository to F-Droid

On your phone, [open the repository link](https://fdroid.link/#https://panlelapin.github.io/fdroidrepo/?fingerprint=363DEB527CD0C41ABBC30359005EE6F2A5A6869716D32CF42CEED66DCC3A7A7A) and confirm the addition in F-Droid. If you are viewing this page on another device, scan the QR code with your phone.

<a href="https://fdroid.link/#https://panlelapin.github.io/fdroidrepo/?fingerprint=363DEB527CD0C41ABBC30359005EE6F2A5A6869716D32CF42CEED66DCC3A7A7A"><img src="index.png" width="265" height="265" alt="QR code to add the signed Pan le lapin repository to F-Droid"></a>

| Repository information | Value |
|---|---|
| Name in F-Droid | Pan le lapin |
| Repository URL | `https://panlelapin.github.io/fdroidrepo/` |
| Signing key fingerprint (SHA-256) | `363DEB527CD0C41ABBC30359005EE6F2A5A6869716D32CF42CEED66DCC3A7A7A` |

Source repository: [panlelapin/fdroidrepo](https://github.com/panlelapin/fdroidrepo). The default branch is `master`.

If you added the repository before this migration, add the URL above. The previous GitHub Pages address may no longer work. The repository signing key has not changed.

## Available apps

- [**BlackBG**](https://github.com/panlelapin/blackbg/releases/latest) (`com.github.panlelapin.blackbg`): a static black wallpaper.
- [**WFQA**](https://github.com/panlelapin/wfqa/releases/latest) (`com.github.panlelapin.wfqa`): offline quick capture for WorkFlowy.

These package identifiers replace `app.blackbg` and `io.github.panlelapin.wfquickadd`. Android treats them as new apps. Before uninstalling the older WFQA app, allow it to finish sending all queued entries.

## Publish an update

In the app's repository, increment its version and `versionCode`, then publish a stable release tagged `v<version>`. The app's workflow builds and signs the APK before attaching it to the release. Signing runs in a separate job, isolated from the build.

The [Update the Pan le lapin repository](https://github.com/panlelapin/fdroidrepo/actions/workflows/catalog.yml) workflow checks for new APKs every 15 minutes; GitHub may delay scheduled runs. If a release's signed APK is not ready, the workflow checks again on the next run. To publish immediately after signing, open the workflow and select **Run workflow**. Manual runs also regenerate the index and verify its signing certificate.

Allowed source repositories, package identifiers, asset names, and APK signing fingerprints are defined in `catalog/apps.json`. Already indexed APKs are skipped. A different APK reusing an existing `versionCode` is rejected. This repository's Actions secrets contain only the index signing key and its password. Each app repository retains its own APK signing secrets; no shared personal access token is required.

## Repository layout and tests

Public F-Droid assets are stored at the repository root. Import, signing, and staging tools, tests, and app descriptions are maintained in `catalog/`. GitHub Pages receives only public assets, not the source tooling.

Run the test suite with:

```sh
python3 -B -m unittest discover -s catalog -v
```
