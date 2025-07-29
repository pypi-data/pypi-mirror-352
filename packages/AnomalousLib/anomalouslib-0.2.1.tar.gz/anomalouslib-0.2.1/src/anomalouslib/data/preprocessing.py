from anomalouslib.constants import trajectory_types_mapping

from sklearn.preprocessing import LabelEncoder
import torch.nn.functional as F
import numpy as np
import torch

def _min_max_params(trajectory_type, parm_to_eval):
    type_constants = trajectory_types_mapping[trajectory_type]
    min_attr = f"min_{parm_to_eval}"
    max_attr = f"max_{parm_to_eval}"
    min_value = getattr(type_constants, min_attr)
    max_value = getattr(type_constants, max_attr)
    if min_value is None or max_value is None:
        raise ValueError(f"Min or Max value for {parm_to_eval} not defined in {trajectory_type}.")
    if min_value >= max_value:
        raise ValueError(f"Min value {min_value} must be less than Max value {max_value} for {parm_to_eval} in {trajectory_type}.")
    return min_value, max_value

def min_max_normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

def generate_tensors(dataframe, trajectory_type, parm_to_eval: str):
    # Aconseguim un dataframe amb les coordenades i la hurst
    df = dataframe[["coords", "attributes"]].copy()
    df[parm_to_eval] = df["attributes"].apply(lambda x: x[parm_to_eval])
    df = df[["coords", parm_to_eval]]

    # Tractem les coordenades per aconseguir X_tensor
    coords_list = [np.stack([row[0], row[1]], axis=1) for row in df['coords']]
    X = np.array(coords_list)  # Forma (n_samples, seq_length, 2)
    # Per aconseguir la forma (n_samples, 2, seq_length)
    X_tensor = torch.tensor(X, dtype=torch.float32).permute(0, 2, 1)

    # Tractem les coordenades per aconseguir y_tensor
    min_value, max_value = _min_max_params(trajectory_type, parm_to_eval)
    hurst_series = df[parm_to_eval].apply(lambda x: min_max_normalize(x, min_value, max_value))
    labels = hurst_series.values  # Suponiendo que 'hurst' contiene los valores reales
    y_tensor = torch.tensor(labels, dtype=torch.float32).unsqueeze(1)

    return X_tensor, y_tensor

def generate_classification_tensors(dataframe, parm_to_eval: str, le = LabelEncoder()):
    # dataframe = dataframe.drop(columns=['num_steps', 'attributes'])
    dataframe = dataframe.sample(frac=1).reset_index(drop=True)

    # Tractem les coordenades per aconseguir X_tensor
    coords_list = [np.stack([row[0], row[1]], axis=1) for row in dataframe['coords']]
    X = np.array(coords_list)  # Forma (n_samples, seq_length, 2)
    X_tensor = torch.tensor(X, dtype=torch.float32).permute(0, 2, 1)

    # Tractem les coordenades per aconseguir y_tensor
    labels = le.transform(dataframe["attributes"].apply(lambda x: x[parm_to_eval]))
    labels_tensor  = torch.tensor(labels, dtype=torch.long)
    y_tensor = F.one_hot(labels_tensor, num_classes=7).float()

    return X_tensor, y_tensor
