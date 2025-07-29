Le nœud CLIPSave est conçu pour sauvegarder les modèles CLIP ainsi que des informations supplémentaires telles que les prompts et les métadonnées PNG. Il encapsule la fonctionnalité de sérialisation et de stockage de l'état du modèle, facilitant la préservation et le partage des configurations de modèle et de leurs prompts créatifs associés.
## Types d'entrée

| Paramètre | Comfy dtype | Description |
|-----------|-------------|-------------|
| `clip`    | `CLIP`      | Le modèle CLIP à sauvegarder. Ce paramètre est crucial car il représente le modèle dont l'état doit être sérialisé et stocké. |
| `filename_prefix` | `STRING` | Un préfixe pour le nom de fichier sous lequel le modèle et ses informations supplémentaires seront sauvegardés. Ce paramètre permet un stockage organisé et une récupération facile des modèles sauvegardés. |

## Types de sortie

Le nœud n'a pas de types de sortie.
