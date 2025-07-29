
This node is designed for advanced model merging operations, specifically to subtract the parameters of one model from another based on a specified multiplier. It enables the customization of model behaviors by adjusting the influence of one model's parameters over another, facilitating the creation of new, hybrid models.
## Input types

| Parameter     | Comfy dtype | Description |
|---------------|--------------|-------------|
| `model1`      | `MODEL`     | The base model from which parameters will be subtracted. |
| `model2`      | `MODEL`     | The model whose parameters will be subtracted from the base model. |
| `multiplier`  | `FLOAT`     | A floating-point value that scales the subtraction effect on the base model's parameters. |

## Output types

| Parameter | Comfy dtype | Description |
|-----------|-------------|-------------|
| `model`   | `MODEL`     | The resulting model after subtracting the parameters of one model from another, scaled by the multiplier. |