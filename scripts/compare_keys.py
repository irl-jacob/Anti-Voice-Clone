import torch
import onnx
import sys
sys.path.append("/projects/Dhwani-Deepfake-Audio-Detection-API/src/model")
from architecture import DeepfakeDetectorModel

model = DeepfakeDetectorModel()
pt_keys = list(model.state_dict().keys())

onnx_model = onnx.load("/projects/avc/ai/best_model.onnx", load_external_data=False)
onnx_keys = [i.name for i in onnx_model.graph.initializer]

print("PyTorch keys (first 10):", pt_keys[:10])
print("ONNX keys (first 10):", onnx_keys[:10])
print("Matches?", set(pt_keys) == set(onnx_keys))
print("Missing in ONNX:", set(pt_keys) - set(onnx_keys))
print("Missing in PyTorch:", set(onnx_keys) - set(pt_keys))
