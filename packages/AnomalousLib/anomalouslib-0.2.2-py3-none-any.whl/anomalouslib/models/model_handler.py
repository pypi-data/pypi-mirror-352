import torch.nn.functional as F
import torch.nn as nn
import inspect
import torch
import dill
import os

def get_class_def_from_notebook(class_name: str):
    from IPython import get_ipython
    shell = get_ipython()
    for cell in shell.history_manager.get_range():
        if class_name in cell[2]:
            return cell[2]
    return None

def load_model(model_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(model_path, map_location=device, pickle_module=dill)
    
    # Executem el codi font per recrear la clase
    exec(checkpoint["model_source"], globals())  # La clase es definex a l'escope global
    
    # Instanciar el model amb els seus arguments originals
    model_class = globals()[checkpoint["model_source"].split("class ")[1].split("(")[0].strip()]
    model = model_class(**checkpoint["params"])
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device)
    model.eval()
    if checkpoint.get("le") is not None:
        return model, checkpoint["le"]
    return model

def load_model_name(model_path):
    checkpoint = torch.load(model_path, map_location=device, pickle_module=dill)
    return checkpoint["model_name"]

def save_model(model_instance, model_type,  model_source, params, input_channels, model_name=None, path=None, le=None):
    if model_name is None:
        model_name = model_instance.__class__.__name__
    filename = f"{model_name}.pth"
    if path is not None:
        os.makedirs(path, exist_ok=True)
        save_path = os.path.join(path, filename)
    else:
        save_path = filename
    torch.save({
        "model_name": model_name,
        "model_type": model_type,
        "model_source": model_source,
        "state_dict": model_instance.state_dict(),
        "params": params,
        "input_channels": input_channels
        , **({"le": le} if le is not None else {})
    }, save_path, pickle_module=dill)


