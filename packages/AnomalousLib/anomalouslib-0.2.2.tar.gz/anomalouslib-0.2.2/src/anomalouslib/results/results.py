from typing import Any
import pickle

# Clase para gestionar resultados
class ResultManager:
    def __init__(self):
        self.results = {}
    
    def add_result(self, name: str, result: Any):
        self.results[name] = result
    
    def save_results(self, path: str, format: str = 'pickle'):
        """Guarda los resultados en diferentes formatos"""
        if format == 'pickle':
            with open(path, 'wb') as f:
                pickle.dump(self.results, f)
        elif format == 'txt':
            with open(path, 'w') as f:
                for name, result in self.results.items():
                    f.write(f"{name}:\n{str(result)}\n\n")
        else:
            raise ValueError(f"Formato no soportado: {format}")
