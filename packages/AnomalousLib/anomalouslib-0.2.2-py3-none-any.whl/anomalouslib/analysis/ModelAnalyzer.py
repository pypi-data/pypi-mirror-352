from matplotlib.widgets import TextBox
import matplotlib.pyplot as plt
import numpy as np
from anomalouslib.constants import trajectory_types_mapping
import torch
import torch.nn.functional as F

# Classe per a l'anàlisi de dades
class ModelAnalyzer:
    def __init__(self, dataset):
        self.dataset = dataset

    def analyze_discrete_trajectory_patterns(self, model, parm_to_eval, le, traj_pos=0, window_size=150, draw=True):
        dataframe = self.dataset.iloc[[traj_pos]].copy()
        dataframe = dataframe.sample(frac=1).reset_index(drop=True)

        coords_list = [np.stack([row[0], row[1]], axis=1) for row in dataframe['coords']]
        X = np.array(coords_list)
        X_tensor = torch.tensor(X, dtype=torch.float32).permute(0, 2, 1)

        params = dataframe["attributes"].apply(lambda x: x[parm_to_eval])[0]

        def get_correct_type(diccionario, valor):
            if not isinstance(diccionario, dict):
                return diccionario
            claves_ordenadas = sorted(diccionario.keys())
            for i in range(len(claves_ordenadas)):
                inicio = claves_ordenadas[i]
                fin = claves_ordenadas[i + 1] if i + 1 < len(claves_ordenadas) else float('inf')
                if inicio <= valor < fin:
                    return diccionario[inicio]
            return None

        with torch.no_grad():
            out = model(X_tensor)
            predicted_class = torch.argmax(out, dim=1).item()

        X_unfolded = X_tensor.unfold(dimension=2, size=window_size, step=1)
        X_windows = X_unfolded.permute(2, 0, 1, 3)
        X_list = [x for x in X_windows]

        X_adjusted = []
        for window in X_list:
            start = window[:, :, 0].unsqueeze(-1)
            adjusted = window - start
            X_adjusted.append(adjusted)

        model.eval()
        outputs = []
        values = []
        with torch.no_grad():
            for x in X_adjusted:
                out = model(x)
                out = F.softmax(out, dim=1)
                predicted_class = torch.argmax(out, dim=1).item()
                array = out.numpy()[0]
                outputs.append(np.array(array))
                values.append(le.inverse_transform([predicted_class])[0])

        outputs = np.array(outputs)
        long_names = le.inverse_transform(np.arange(outputs.shape[1]))
        short_pattern_names = np.array([trajectory_types_mapping[long_name].__name__ for long_name in long_names])

        fig, axs = plt.subplots(2, 1, figsize=(12, 6))

        if outputs.size > 0:
            for i in range(outputs.shape[1]):
                axs[0].plot(outputs[:, i], label=f'{short_pattern_names[i]}')
            axs[0].set_title('Evolución de probabilidades de los patrones')
            axs[0].set_xlabel('Ventana temporal')
            axs[0].set_ylabel('Probabilidad')
            axs[0].legend()

            patron_dominante = np.argmax(outputs, axis=1)
            axs[1].plot(patron_dominante, 'o-', label='Patrón dominante')

            correct_classes = []
            correct_labels = []
            correct_shorts = []
            for i in range(len(outputs)):
                current_label = get_correct_type(params, i + window_size // 2)
                if current_label:
                    correct_labels.append(current_label)
                    correct_class = le.transform([current_label])[0]
                    correct_classes.append(correct_class)
                    correct_shorts.append(trajectory_types_mapping[current_label].__name__)
                else:
                    correct_classes.append(None)
                    correct_shorts.append(None)

            axs[1].plot(correct_classes, color='red', linestyle='--', label='Respuesta correcta')
            axs[1].set_title('Cambios en el patrón dominante')
            axs[1].set_xlabel('Ventana temporal')
            axs[1].set_ylabel('Patrón detectado')
            axs[1].set_yticks(np.arange(outputs.shape[1]))
            axs[1].set_yticklabels(short_pattern_names)
            axs[1].legend()

        plt.tight_layout()
        if draw:
            plt.show()
        return plt, fig, axs

    def analyze_continuous_trajectory_patterns(self, model, parm_to_eval, traj_pos=0, window_size=150, draw=True):
        dataframe = self.dataset.iloc[[traj_pos]].copy()
        dataframe = dataframe.sample(frac=1).reset_index(drop=True)

        coords_list = [np.stack([row[0], row[1]], axis=1) for row in dataframe['coords']]
        X = np.array(coords_list)
        X_tensor = torch.tensor(X, dtype=torch.float32).permute(0, 2, 1)

        params = dataframe["attributes"].apply(lambda x: x[parm_to_eval])[0]

        def get_correct_type(diccionario, valor):
            claves_ordenadas = sorted(diccionario.keys())
            for i in range(len(claves_ordenadas)):
                inicio = claves_ordenadas[i]
                fin = claves_ordenadas[i + 1] if i + 1 < len(claves_ordenadas) else float('inf')
                if inicio <= valor < fin:
                    return diccionario[inicio]
            return None

        X_unfolded = X_tensor.unfold(dimension=2, size=window_size, step=1)
        X_windows = X_unfolded.permute(2, 0, 1, 3)
        X_list = [x for x in X_windows]

        X_adjusted = []
        for window in X_list:
            start = window[:, :, 0].unsqueeze(-1)
            adjusted = window - start
            X_adjusted.append(adjusted)

        model.eval()
        predictions = []
        with torch.no_grad():
            for x in X_adjusted:
                pred = model(x)
                predictions.append(pred.item())

        predictions = np.array(predictions)

        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(predictions, label='Predicción del modelo')
        ax.set_title('Evolución de la predicción del modelo')
        ax.set_xlabel('Ventana temporal')
        ax.set_ylabel('Valor predicho')
        ax.legend()
        plt.tight_layout()
        if draw:
            plt.show()

        return plt, fig, ax
