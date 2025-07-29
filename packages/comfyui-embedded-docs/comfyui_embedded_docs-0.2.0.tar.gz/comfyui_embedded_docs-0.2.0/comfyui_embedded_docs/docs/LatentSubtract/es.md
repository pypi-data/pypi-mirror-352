
El nodo LatentSubtract está diseñado para restar una representación latente de otra. Esta operación se puede utilizar para manipular o modificar las características de las salidas de modelos generativos eliminando efectivamente características o atributos representados en un espacio latente de otro.
## Tipos de entrada

| Parámetro    | Comfy dtype | Descripción |
|--------------|-------------|-------------|
| `samples1`   | `LATENT`    | El primer conjunto de muestras latentes del cual se restará. Sirve como base para la operación de resta. |
| `samples2`   | `LATENT`    | El segundo conjunto de muestras latentes que se restará del primer conjunto. Esta operación puede alterar la salida del modelo generativo resultante eliminando atributos o características. |

## Tipos de salida

| Parámetro | Comfy dtype | Descripción |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | El resultado de restar el segundo conjunto de muestras latentes del primero. Esta representación latente modificada se puede utilizar para tareas generativas adicionales. |