This node will detect models located in the `ComfyUI/models/checkpoints` folder, and it will also read models from additional paths configured in the extra_model_paths.yaml file. Sometimes, you may need to **refresh the ComfyUI interface** to allow it to read the model files from the corresponding folder.


This node specializes in loading checkpoints specifically for image-based models within video generation workflows. It efficiently retrieves and configures the necessary components from a given checkpoint, focusing on image-related aspects of the model.
## Input types

| Field      | Comfy dtype | Description                                                                       |
|------------|-------------|-----------------------------------------------------------------------------------|
| `ckpt_name`| `COMBO[STRING]` | Specifies the name of the checkpoint to load, crucial for identifying and retrieving the correct checkpoint file from a predefined list. |

## Output types

| Field     | Comfy dtype | Description                                                                                   |
|-----------|-------------|-----------------------------------------------------------------------------------------------|
| `model`   | `MODEL`     | Returns the main model loaded from the checkpoint, configured for image processing within video generation contexts. |
| `clip_vision` | `CLIP_VISION` | Provides the CLIP vision component from the checkpoint, tailored for image understanding and feature extraction. |
| `vae`     | `VAE`       | Delivers the Variational Autoencoder (VAE) component, essential for image manipulation and generation tasks. |