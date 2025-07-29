
El nodo `MaskToImage` está diseñado para convertir una máscara en un formato de imagen. Esta transformación permite la visualización y el procesamiento adicional de máscaras como imágenes, facilitando un puente entre las operaciones basadas en máscaras y las aplicaciones basadas en imágenes.
## Tipos de entrada
| Parámetro | Comfy dtype | Descripción |
|-----------|-------------|-------------|
| `mask`    | `MASK`      | La entrada de máscara es esencial para el proceso de conversión, sirviendo como los datos fuente que se transformarán en un formato de imagen. Esta entrada dicta la forma y el contenido de la imagen resultante. |

## Tipos de salida
| Parámetro | Comfy dtype | Descripción |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | La salida es una representación de imagen de la máscara de entrada, permitiendo la inspección visual y manipulaciones adicionales basadas en imágenes. |