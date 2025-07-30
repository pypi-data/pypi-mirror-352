import torch
from transformers import (
    ViTMAEConfig,
    ViTMAEForPreTraining,
)


class HealFormerConfig(ViTMAEConfig): ...


class HealFormerModel(ViTMAEForPreTraining): ...
