
Le nœud SolidMask génère un masque uniforme avec une valeur spécifiée sur toute sa surface. Il est conçu pour créer des masques de dimensions et d'intensité spécifiques, utiles dans diverses tâches de traitement d'image et de masquage.
## Types d'entrée

| Paramètre | Comfy dtype | Description |
|-----------|-------------|-------------|
| `value`   | FLOAT       | Spécifie la valeur d'intensité du masque, affectant son apparence générale et son utilité dans les opérations ultérieures. |
| `width`   | INT         | Détermine la largeur du masque généré, influençant directement sa taille et son rapport d'aspect. |
| `height`  | INT         | Définit la hauteur du masque généré, affectant sa taille et son rapport d'aspect. |

## Types de sortie

| Paramètre | Comfy dtype | Description |
|-----------|-------------|-------------|
| `mask`    | MASK        | Produit un masque uniforme avec les dimensions et la valeur spécifiées. |