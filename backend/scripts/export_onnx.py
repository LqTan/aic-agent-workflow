from pathlib import Path
import torch
import open_clip

OUT = Path("models/text_encoder.onnx")


class TextEncoder(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, tokens):
        x = self.model.encode_text(tokens)
        return x / x.norm(dim=-1, keepdim=True)


model, _, _ = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="openai",
)

model.eval()

encoder = TextEncoder(model).eval()

dummy = torch.zeros((1, 77), dtype=torch.long)

OUT.parent.mkdir(exist_ok=True)

torch.onnx.export(
    encoder,
    dummy,
    OUT,
    input_names=["tokens"],
    output_names=["clip_text_output"],
    dynamic_axes={
        "tokens": {0: "batch"},
        "clip_text_output": {0: "batch"},
    },
    opset_version=18,
)
