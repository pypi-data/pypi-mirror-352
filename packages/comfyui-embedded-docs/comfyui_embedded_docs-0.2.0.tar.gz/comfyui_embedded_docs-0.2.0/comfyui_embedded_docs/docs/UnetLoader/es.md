

El nodo UNETLoader está diseñado para cargar modelos U-Net por nombre, facilitando el uso de arquitecturas U-Net preentrenadas dentro del sistema.
## Tipos de entrada - Guía del Cargador UNET | Cargar Modelo de Difusión

| Parámetro   | Tipo Comfy  | Descripción |
|-------------|--------------|-------------|
| `unet_name` | `COMBO[STRING]` | Especifica el nombre del modelo U-Net que se va a cargar. Este nombre se utiliza para localizar el modelo dentro de una estructura de directorio predefinida, permitiendo la carga dinámica de diferentes modelos U-Net. |
| `weight_dtype` | ... | 🚧  fp8_e4m3fn fp9_e5m2  |

## Tipos de salida - Guía del Cargador UNET | Cargar Modelo de Difusión

| Parámetro | Tipo Comfy | Descripción |
|-----------|-------------|-------------|
| `model`   | `MODEL`     | Devuelve el modelo U-Net cargado, permitiendo su utilización para procesamiento adicional o inferencia dentro del sistema. |
