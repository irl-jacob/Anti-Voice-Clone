import torch
import onnx
import sys
sys.path.append("/projects/Dhwani-Deepfake-Audio-Detection-API/src/model")
from architecture import DeepfakeDetectorModel

model = DeepfakeDetectorModel()
pt_keys = set(model.state_dict().keys())

onnx_model = onnx.load("/projects/avc/ai/best_model.onnx", load_external_data=False)
onnx_keys = set([i.name for i in onnx_model.graph.initializer])

matched = pt_keys.intersection(onnx_keys)
print(f"Matched exactly: {len(matched)} / {len(pt_keys)} PyTorch keys")
print(f"ONNX initializers total: {len(onnx_keys)}")

missing_in_onnx = pt_keys - onnx_keys
print(f"\nMissing in ONNX (PyTorch has it but ONNX does not, sample 10):", list(missing_in_onnx)[:10])

# Are the missing ones just biases that are zero or folded?
