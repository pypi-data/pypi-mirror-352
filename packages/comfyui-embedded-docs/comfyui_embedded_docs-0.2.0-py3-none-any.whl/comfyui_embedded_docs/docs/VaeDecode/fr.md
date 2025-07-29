
Le nœud VAEDecode est conçu pour décoder les représentations latentes en images en utilisant un Autoencodeur Variationnel (VAE) spécifié. Il sert à générer des images à partir de représentations de données compressées, facilitant la reconstruction d'images à partir de leurs encodages dans l'espace latent.
## Types d'entrée

| Paramètre | Comfy dtype | Description |
|-----------|-------------|-------------|
| `samples` | `LATENT`    | Le paramètre 'samples' représente les représentations latentes à décoder en images. Il est crucial pour le processus de décodage car il fournit les données compressées à partir desquelles les images sont reconstruites. |
| `vae`     | `VAE`       | Le paramètre 'vae' spécifie le modèle d'Autoencodeur Variationnel à utiliser pour décoder les représentations latentes en images. Il est essentiel pour déterminer le mécanisme de décodage et la qualité des images reconstruites. |

## Types de sortie

| Paramètre | Comfy dtype | Description |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | La sortie est une image reconstruite à partir de la représentation latente fournie en utilisant le modèle VAE spécifié. |