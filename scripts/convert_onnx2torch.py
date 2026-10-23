import os
import sys
import torch
import onnx
from onnx2torch import convert

default_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai", "best_model.onnx")
model_path = sys.argv[1] if len(sys.argv) > 1 else default_path

print(f"Loading ONNX from {model_path}...")
onnx_model = onnx.load(model_path, load_external_data=False)
print("Converting to PyTorch...")
torch_model = convert(onnx_model)
print("Done!")
print("Parameters count:", sum(p.numel() for p in torch_model.parameters()))
