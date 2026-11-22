# Pan le lapin — applications Android

[Ajouter le catalogue dans F-Droid](https://panlelapin.github.io/android/fdroid/repo/?fingerprint=363DEB527CD0C41ABBC30359005EE6F2A5A6869716D32CF42CEED66DCC3A7A7A)

- [**BlackBG**](https://github.com/panlelapin/blackbg/releases/latest) (`com.github.panlelapin.blackbg`) : fond d’écran noir.
- [**wfqa**](https://github.com/panlelapin/wfqa/releases/latest) (`com.github.panlelapin.wfqa`) : saisie rapide hors ligne pour WorkFlowy (nom sur Android : **WFQA**).

Ces identifiants remplacent `app.blackbg` et `io.github.panlelapin.wfquickadd` : Android les installe comme de nouvelles applications. Avant de désinstaller l’ancienne WFQA, laisser sa file d’attente se vider.

Adresse : `https://panlelapin.github.io/android/fdroid/repo/`

Empreinte SHA-256 de la clé du catalogue : `363DEB527CD0C41ABBC30359005EE6F2A5A6869716D32CF42CEED66DCC3A7A7A`.

## Publier depuis GitHub

Dans le dépôt de l’application, augmenter sa version et son `versionCode`, puis publier une release stable avec un tag `v<version>`. L’action de l’application construit et signe l’APK avant de le joindre à la release. Le job de signature est isolé du build.

Le workflow [Mettre à jour Pan le lapin](../../actions/workflows/catalogue.yml) recherche les nouveaux APK toutes les 15 minutes (GitHub peut retarder l’exécution). Une release dont l’APK n’est pas encore prêt est reprise au passage suivant. Pour publier immédiatement après la signature, ouvrir ce workflow et choisir **Run workflow**. Le contrôle manuel reconstruit également l’index pour vérifier la clé de signature.

Les sources autorisées, packages, noms d’assets et empreintes de signature sont dans `catalogue/apps.json`. Un APK déjà indexé est ignoré ; un autre APK réutilisant un `versionCode` est refusé. Les secrets Actions de ce dépôt ne contiennent que la clé d’index et son mot de passe. Les deux dépôts d’applications conservent chacun leurs propres secrets de signature. Aucun jeton personnel partagé n’est nécessaire.
