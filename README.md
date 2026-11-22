# Pan le lapin — applications Android

[Ajouter le catalogue dans F-Droid](https://panlelapin.github.io/fdroid-repo/fdroid/repo/?fingerprint=363DEB527CD0C41ABBC30359005EE6F2A5A6869716D32CF42CEED66DCC3A7A7A)

- [**BlackBG**](https://github.com/panlelapin/blackbg/releases/latest) (`com.github.panlelapin.blackbg`) : fond d’écran noir.
- [**wfqa**](https://github.com/panlelapin/wfqa/releases/latest) (`com.github.panlelapin.wfqa`) : saisie rapide hors ligne pour WorkFlowy (nom sur Android : **WFQA**).

Ces identifiants remplacent `app.blackbg` et `io.github.panlelapin.wfquickadd` : Android les installe comme de nouvelles applications. Avant de désinstaller l’ancienne WFQA, laisser sa file d’attente se vider.

Adresse : `https://panlelapin.github.io/fdroid-repo/fdroid/repo/`

Empreinte SHA-256 de la clé du catalogue : `363DEB527CD0C41ABBC30359005EE6F2A5A6869716D32CF42CEED66DCC3A7A7A`.

Pour publier une mise à jour, conserver la clé de signature propre à chaque application et augmenter son `versionCode`. Régénérer l’index dans le dossier privé F-Droid existant avec la même clé d’index. Publier uniquement les fichiers publics sous `fdroid/repo/` sur `main`, après vérification des APK et de l’index signé. Les clés et la configuration privée restent hors Git.
