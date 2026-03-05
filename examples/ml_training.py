# stepcast ml_training.py — ML pipeline example
# Requires: pip install stepcast
from stepcast import Pipeline

pipe = Pipeline("🤖 ML Training Pipeline")


@pipe.step("Load dataset")
def load_data() -> dict:
    # Simulated data loading
    import random
    random.seed(42)
    X = [[random.random(), random.random()] for _ in range(100)]
    y = [1 if x[0] + x[1] > 1 else 0 for x in X]
    print(f"→ Loaded {len(X)} samples, {sum(y)} positive labels")
    return {"X": X, "y": y}


@pipe.step("Split train/test")
def split_data(data: dict) -> dict:
    X, y = data["X"], data["y"]
    split = int(len(X) * 0.8)
    result = {
        "X_train": X[:split], "y_train": y[:split],
        "X_test": X[split:], "y_test": y[split:],
    }
    print(f"→ Train: {split} samples, Test: {len(X) - split} samples")
    return result


@pipe.step("Train model")
def train(data: dict) -> dict:
    # Simulated training (no sklearn required for demo)
    X_train = data["X_train"]
    y_train = data["y_train"]
    # Naive "model": use threshold 1.0 on sum of features
    accuracy = sum(
        1 for x, y in zip(X_train, y_train)
        if (1 if x[0] + x[1] > 1 else 0) == y
    ) / len(y_train)
    print(f"→ Training accuracy: {accuracy:.2%}")
    return {"threshold": 1.0, "train_acc": accuracy}


@pipe.step("Evaluate model")
def evaluate(model: dict) -> dict:
    print(f"→ Model threshold: {model['threshold']}")
    print(f"→ Train accuracy: {model['train_acc']:.2%}")
    print("→ Placeholder: Test accuracy evaluation complete")
    return {"accuracy": model["train_acc"], "status": "evaluated"}


@pipe.step("Save model", skip_if=lambda: False)
def save_model(result: dict) -> None:
    print(f"→ Saving model with accuracy {result['accuracy']:.2%}")
    print("→ Model saved to models/latest.pkl (simulated)")


if __name__ == "__main__":
    report = pipe.run()
    print(f"\n{report.summary()}")
