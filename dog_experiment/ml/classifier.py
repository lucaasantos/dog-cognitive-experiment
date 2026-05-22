"""Prediction helpers for the hybrid cognitive system."""

import pickle
from pathlib import Path


ML_DIR = Path(__file__).resolve().parent
MODEL_FILE = ML_DIR / "model.pkl"

_MODEL = None


def load_model():
    """Load model.pkl, training it from dataset.csv when needed."""
    global _MODEL

    if _MODEL is not None:
        return _MODEL

    if not MODEL_FILE.exists():
        from ml.train_model import train_model

        _MODEL = train_model()
        return _MODEL

    with MODEL_FILE.open("rb") as file:
        _MODEL = pickle.load(file)

    return _MODEL


def classify_experience(text):
    """Return the predicted label and probability confidence for an experience."""
    model = load_model()
    label = str(model.predict([text])[0])
    probabilities = model.predict_proba([text])[0]
    labels = model.classes_
    confidence = float(probabilities[list(labels).index(label)])

    return label, round(confidence, 4)
