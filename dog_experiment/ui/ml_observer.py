"""ML inspection and lightweight learning utilities for the dashboard."""

import csv
from collections import Counter
from pathlib import Path

import pandas as pd

from ml.classifier import load_model
from ml.train_model import DATASET_FILE, train_model


RISK_LABELS = {"aggressive", "threatening", "defensive"}
SAFE_LABELS = {"friendly", "playful", "calm"}


def _pipeline_parts():
    model = load_model()
    return model, model.named_steps["vectorizer"], model.named_steps["classifier"]


def prediction_snapshot(text):
    """Return label, probabilities, active tokens, and class evidence."""
    model, vectorizer, classifier = _pipeline_parts()
    matrix = vectorizer.transform([text])
    probabilities = model.predict_proba([text])[0]
    classes = list(classifier.classes_)
    label = str(model.predict([text])[0])
    confidence = float(probabilities[classes.index(label)])

    names = vectorizer.get_feature_names_out()
    active_indices = matrix.nonzero()[1]
    active_tokens = [names[index] for index in active_indices]

    class_index = classes.index(label)
    evidence = []
    for token in active_tokens:
        token_index = vectorizer.vocabulary_.get(token)
        if token_index is None:
            continue
        evidence.append((token, float(classifier.feature_log_prob_[class_index][token_index])))
    evidence.sort(key=lambda item: item[1], reverse=True)

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "classes": classes,
        "probabilities": {classes[index]: float(probabilities[index]) for index in range(len(classes))},
        "active_tokens": active_tokens[:12],
        "evidence": evidence[:8],
    }


def top_tokens(limit=5):
    """Return top learned tokens for risk-oriented and safe classes."""
    _model, vectorizer, classifier = _pipeline_parts()
    names = vectorizer.get_feature_names_out()

    def best_for(labels):
        rows = [list(classifier.classes_).index(label) for label in labels if label in classifier.classes_]
        if not rows:
            return []
        scores = classifier.feature_log_prob_[rows].max(axis=0)
        ranked = scores.argsort()[-limit * 3:][::-1]
        tokens = []
        for index in ranked:
            token = names[index]
            if " " not in token and token not in tokens:
                tokens.append(token)
            if len(tokens) == limit:
                break
        return tokens

    return {
        "aggressive": best_for(RISK_LABELS),
        "friendly": best_for(SAFE_LABELS),
    }


def dataset_stats(dataset_file=DATASET_FILE):
    """Return dataset size and class distribution."""
    path = Path(dataset_file)
    if not path.exists():
        return {"total": 0, "distribution": {}, "risk": 0, "safe": 0, "ratio": "0:0"}

    data = pd.read_csv(path)
    distribution = Counter(data["label"]) if "label" in data else Counter()
    risk = sum(distribution[label] for label in RISK_LABELS)
    safe = sum(distribution[label] for label in SAFE_LABELS)
    return {
        "total": int(len(data)),
        "distribution": dict(distribution),
        "risk": int(risk),
        "safe": int(safe),
        "ratio": f"{risk}:{safe}",
    }


def append_and_retrain(text, label, dataset_file=DATASET_FILE):
    """Append the classified experience to the local dataset and retrain."""
    if not label or label == "unavailable":
        return None

    path = Path(dataset_file)
    has_header = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["text", "label"])
        if not has_header:
            writer.writeheader()
        writer.writerow({"text": text, "label": label})

    model = train_model(dataset_file=path)

    import ml.classifier as classifier_module

    classifier_module._MODEL = model
    return model
