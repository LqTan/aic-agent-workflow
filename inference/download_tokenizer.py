from pathlib import Path
from transformers import CLIPTokenizerFast

output = Path("models/tokenizer")

tokenizer = CLIPTokenizerFast.from_pretrained(
    "openai/clip-vit-base-patch32"
)

tokenizer.save_pretrained(output)

print(f"Saved tokenizer to {output}")
