import torch
import copy

def _get_loss_name(criterion):
    # Puedes añadir más casos según tus criterios
    name_map = {
        "CrossEntropyLoss": "CE Loss",
        "MSELoss": "MSE Loss",
        "BCELoss": "BCE Loss",
        "BCEWithLogitsLoss": "BCEWithLogits Loss"
    }
    crit_name = type(criterion).__name__
    return name_map.get(crit_name, "Loss")

def train_model(model, train_loader, criterion, optimizer, patience=None, num_epochs=50, val_loader=None, scheduler=None, print_epoch=True):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    best_val_loss = float('inf')
    counter = 0
    loss_name = _get_loss_name(criterion)
    best_model = copy.deepcopy(model)

    for epoch in range(num_epochs):
        # Entrenamiento
        model.train()
        train_loss = 0.0
        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
            train_loss += loss.item() * inputs.size(0)
        
        train_loss /= len(train_loader.dataset)

        # Validación solo si val_loader está definido
        val_loss = None
        if val_loader is not None:
            model.eval()
            val_loss = 0.0
            # correct = 0
            # total = 0
            with torch.no_grad():
                for inputs, labels in val_loader:
                    inputs, labels = inputs.to(device), labels.to(device)
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    val_loss += loss.item() * inputs.size(0)
            val_loss /= len(val_loader.dataset)

        # Actualización del scheduler (dependiendo de su tipo)
        if scheduler is not None:
            if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                if val_loss is not None:
                    scheduler.step(val_loss)  # Scheduler basado en métrica
                else:
                    print("Warning: ReduceLROnPlateau necesita val_loader para funcionar.")
            else:
                scheduler.step()  # Scheduler basado en tiempo/iteración

        # Logging
        if print_epoch:
            log = f"Epoch {epoch+1}/{num_epochs}\nTrain {loss_name}: {train_loss:.4f}"
            if val_loader is not None:
                log += f" | Val {loss_name}: {val_loss:.4f}"
            print(log)
            
        # Early stopping (solo si hay validación)
        if val_loader is not None and patience is not None:
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_model = copy.deepcopy(model)
                counter = 0
            else:
                counter += 1
                if counter >= patience:
                    print("Early stopping!")
                    break
    return best_model