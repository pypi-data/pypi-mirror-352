This node specializes in merging two CLIP models based on a specified ratio, effectively blending their characteristics. It selectively applies patches from one model to another, excluding specific components like position IDs and logit scale, to create a hybrid model that combines features from both source models.
## Input types

| Parameter | Comfy dtype | Description |
|-----------|-------------|-------------|
| `clip1`   | `CLIP`      | The first CLIP model to be merged. It serves as the base model for the merging process. |
| `clip2`   | `CLIP`      | The second CLIP model to be merged. Its key patches, except for position IDs and logit scale, are applied to the first model based on the specified ratio. |
| `ratio`   | `FLOAT`     | Determines the proportion of features from the second model to blend into the first model. A ratio of 1.0 means fully adopting the second model's features, while 0.0 retains only the first model's features. |

## Output types

| Parameter | Comfy dtype | Description |
|-----------|-------------|-------------|
| `clip`    | `CLIP`      | The resulting merged CLIP model, incorporating features from both input models according to the specified ratio. |