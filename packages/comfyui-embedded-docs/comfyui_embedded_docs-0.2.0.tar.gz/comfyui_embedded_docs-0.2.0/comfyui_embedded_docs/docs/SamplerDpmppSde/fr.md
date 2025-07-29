
Ce nœud est conçu pour générer un échantillonneur pour le modèle DPM++ SDE (Équation Différentielle Stochastique). Il s'adapte aux environnements d'exécution CPU et GPU, optimisant l'implémentation de l'échantillonneur en fonction du matériel disponible.
## Types d'entrée

| Paramètre      | Comfy dtype | Description |
|----------------|-------------|-------------|
| `eta`          | FLOAT       | Spécifie la taille des pas pour le solveur SDE, influençant la granularité du processus d'échantillonnage.|
| `s_noise`      | FLOAT       | Détermine le niveau de bruit à appliquer pendant le processus d'échantillonnage, affectant la diversité des échantillons générés.|
| `r`            | FLOAT       | Contrôle le ratio de réduction du bruit dans le processus d'échantillonnage, impactant la clarté et la qualité des échantillons générés.|
| `noise_device` | COMBO[STRING]| Sélectionne l'environnement d'exécution (CPU ou GPU) pour l'échantillonneur, optimisant la performance en fonction du matériel disponible.|

## Types de sortie

| Paramètre    | Comfy dtype | Description |
|----------------|-------------|-------------|
| `sampler`    | SAMPLER     | L'échantillonneur généré configuré avec les paramètres spécifiés, prêt à être utilisé dans les opérations d'échantillonnage. |