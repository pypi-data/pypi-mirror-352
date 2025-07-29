import pandas as pd
import pickle
import os

def _ensure_extension(file_name, extension):
    if not file_name.lower().endswith(extension):
        return file_name + extension
    return file_name

def load_from_pickle(path, file_name):
    with open(os.path.join(path, file_name), "rb") as f:
        return pickle.load(f)

def save_to_pickle(value, path, file_name):
    file_name = _ensure_extension(file_name, ".pkl")
    with open(os.path.join(path, file_name), "wb") as f:
        pickle.dump(value, f)

def load_from_csv(path, file_name):
    file_name = _ensure_extension(file_name, ".csv")
    return pd.read_csv(os.path.join(path, file_name))

def save_to_csv(value, path, file_name):
    file_name = _ensure_extension(file_name, ".csv")
    with open(os.path.join(path, file_name), "w", newline='') as f:
        value.to_csv(f, index=False)

