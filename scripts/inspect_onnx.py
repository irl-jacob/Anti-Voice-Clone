import onnx
import sys

def inspect_model(onnx_path):
    print(f"Loading {onnx_path}...")
    model = onnx.load(onnx_path, load_external_data=False)
    
    print(f"IR Version: {model.ir_version}")
    for imp in model.opset_import:
        print(f"Opset [{imp.domain}]: {imp.version}")
        
    print(f"Nodes: {len(model.graph.node)}")
    print(f"Initializers: {len(model.graph.initializer)}")
    
    print("\n--- Inputs ---")
    for i in model.graph.input:
        shape = []
        for d in i.type.tensor_type.shape.dim:
            if d.HasField("dim_value"):
                shape.append(str(d.dim_value))
            elif d.HasField("dim_param"):
                shape.append(d.dim_param)
            else:
                shape.append("?")
        print(f"Name: {i.name}, Type: {i.type.tensor_type.elem_type}, Shape: {shape}")
        
    print("\n--- Outputs ---")
    for o in model.graph.output:
        shape = []
        for d in o.type.tensor_type.shape.dim:
            if d.HasField("dim_value"):
                shape.append(str(d.dim_value))
            elif d.HasField("dim_param"):
                shape.append(d.dim_param)
            else:
                shape.append("?")
        print(f"Name: {o.name}, Type: {o.type.tensor_type.elem_type}, Shape: {shape}")
        
if __name__ == "__main__":
    import os
    default_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai", "best_model.onnx")
    model_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    inspect_model(model_path)
