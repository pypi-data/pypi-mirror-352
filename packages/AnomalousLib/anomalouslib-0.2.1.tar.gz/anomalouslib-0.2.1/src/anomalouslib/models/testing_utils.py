import pandas as pd
import torch

def evaluate_discrete(model, X_test, y_test):
    model.eval()
    with torch.no_grad():
        outputs = model(X_test)
        _, predicted = torch.max(outputs, 1)
        true_labels = torch.argmax(y_test, dim=1)
        accuracy = (predicted == true_labels).float().mean()
    print(f'Test Accuracy: {accuracy.item():.4f}')
    return accuracy.item()

def evaluate_continuous(model, X_test, y_test):
    model.eval()
    with torch.no_grad():
        outputs = model(X_test)
        mse = torch.nn.functional.mse_loss(outputs, y_test)
    print(f'Test MSE: {mse.item():.4f}')
    return mse.item()

def predict_discrete(model, X_input, y_input=None, le=None, single_example=False):
    # Si es un solo ejemplo, añadir dimensión batch
    if single_example:
        X_input = X_input.unsqueeze(0)
        if y_input is not None:
            y_input = y_input.unsqueeze(0)

    model.eval()
    with torch.no_grad():
        output = model(X_input)
        predicted_class = torch.argmax(output, dim=1).cpu().numpy()

    print("Predicción (índice de clase):", predicted_class)
    if le is not None:
        print("Clase predicha:", le.inverse_transform(predicted_class))
    if y_input is not None and le is not None:
        true_class = torch.argmax(y_input, dim=1).cpu().numpy()
        print("Clase real:", le.inverse_transform(true_class))

def predict_continuous(model, X_input, y_input=None, num_samples=None, to_print=True):
    if num_samples is not None:
        X_input = X_input[:num_samples]
        if y_input is not None:
            y_input = y_input[:num_samples]

    model.eval()
    with torch.no_grad():
        output = model(X_input)
        predicted_value = output.cpu().numpy()

    results = {'Prediction': predicted_value.flatten()}
    if y_input is not None:
        true_values = y_input.cpu().numpy().flatten()
        results['Real Value'] = true_values

    df = pd.DataFrame(results)

    if to_print:
        print("Predicciones:")
        for i, row in df.iterrows():
            if 'Valor real' in df.columns:
                print(f"Ejemplo {i+1}: Predicho = {row['Predicción']}, Real = {row['Valor real']}")
            else:
                print(f"Ejemplo {i+1}: Predicho = {row['Predicción']}")

    return df