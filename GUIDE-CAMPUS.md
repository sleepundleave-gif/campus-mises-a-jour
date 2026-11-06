# Campus Android — mises à jour GitHub

Le dépôt public [sleepundleave-gif/campus-mises-a-jour](https://github.com/sleepundleave-gif/campus-mises-a-jour) contient le système de publication. L’APK de départ est publié dans la [release v1.3.0](https://github.com/sleepundleave-gif/campus-mises-a-jour/releases/tag/v1.3.0).

## Activer sur un téléphone

1. Téléchargez `Campus-Android-v1.3.apk` depuis la release et installez-le **sans désinstaller** l’ancienne application, afin de conserver les données et la clé IA locales.
2. Ouvrez Campus, puis **Paramètres → Mises à jour de Campus**.
3. Copiez et enregistrez l’adresse suivante :

```text
https://raw.githubusercontent.com/sleepundleave-gif/campus-mises-a-jour/main/update.json
```

4. Appuyez sur **Vérifier**. Comme la version 1.3 est déjà installée, Campus doit indiquer qu’elle est à jour. L’adresse est à enregistrer une seule fois sur chaque téléphone.

Les futures vérifications auront lieu à l’ouverture de l’application ou en appuyant sur Vérifier. Une mise à jour détectée doit être téléchargée puis installée avec confirmation d’Android. Il n’y a pas d’installation silencieuse ou de notification push lorsque l’application est fermée.

## Pour publier une prochaine version

Construisez un APK Campus avec un `versionCode` supérieur, le même certificat de signature que la version installée, et les architectures ARM 32 et 64 bits. Publiez une release GitHub avec un tag correspondant au `versionName`, par exemple `v1.4.0`, et joignez un seul APK. GitHub Actions vérifiera la signature, l’architecture, le paquet et la version, puis actualisera `update.json`. Consultez l’onglet **Actions** pour contrôler la publication. L’APK doit être accessible publiquement, comme le dépôt.

La clé privée de signature doit être conservée en sécurité et ne doit jamais être publiée. Sans la même clé, les appareils refuseront la mise à jour. L’APK actuel est une version d’essai signée en mode débogage : pour une diffusion réelle, il faut prévoir une signature de production et une migration spécifique des installations existantes.

Le manifeste public, l’empreinte de l’APK et l’action GitHub ont été vérifiés. L’installation de bout en bout n’a pas été testée sur un téléphone dans cet environnement.
