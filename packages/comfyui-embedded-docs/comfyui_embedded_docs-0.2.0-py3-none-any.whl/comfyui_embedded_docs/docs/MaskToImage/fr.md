
Le nœud `MaskToImage` est conçu pour convertir un masque en format image. Cette transformation permet la visualisation et le traitement ultérieur des masques en tant qu'images, facilitant ainsi un pont entre les opérations basées sur les masques et les applications basées sur les images.
## Types d'entrée
| Paramètre | Comfy dtype | Description |
|-----------|-------------|-------------|
| `mask`    | `MASK`      | L'entrée du masque est essentielle pour le processus de conversion, servant de données source qui seront transformées en format image. Cette entrée dicte la forme et le contenu de l'image résultante. |

## Types de sortie
| Paramètre | Comfy dtype | Description |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | La sortie est une représentation image du masque d'entrée, permettant l'inspection visuelle et d'autres manipulations basées sur l'image. |