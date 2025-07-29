This node zeroes out specific elements within the conditioning data structure, effectively neutralizing their influence in subsequent processing steps. It's designed for advanced conditioning operations where direct manipulation of the conditioning's internal representation is required.

## Input types

| Parameter | Comfy dtype                | Description |
|-----------|----------------------------|-------------|
| `conditioning` | `CONDITIONING` | The conditioning data structure to be modified. This node zeroes out the 'pooled_output' elements within each conditioning entry, if present. |

## Output types

| Parameter | Comfy dtype                | Description |
|-----------|----------------------------|-------------|
| `conditioning` | `CONDITIONING` | The modified conditioning data structure, with 'pooled_output' elements set to zero where applicable. |

