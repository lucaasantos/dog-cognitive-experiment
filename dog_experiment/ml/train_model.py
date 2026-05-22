"""Train the dog-experience text classifier.

The model is intentionally lightweight: CountVectorizer converts text into word
counts, and MultinomialNB learns label probabilities from the local dataset.
"""

import pickle
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


ML_DIR = Path(__file__).resolve().parent
DATASET_FILE = ML_DIR / "dataset.csv"
MODEL_FILE = ML_DIR / "model.pkl"


def train_model(dataset_file=DATASET_FILE, model_file=MODEL_FILE):
    """Load dataset.csv, train the classifier pipeline, and save model.pkl."""
    data = pd.read_csv(dataset_file)

    if not {"text", "label"}.issubset(data.columns):
        raise ValueError("dataset.csv must contain text and label columns")

    pipeline = Pipeline(
        [
            ("vectorizer", CountVectorizer(ngram_range=(1, 2), lowercase=True)),
            ("classifier", MultinomialNB()),
        ]
    )
    pipeline.fit(data["text"], data["label"])

    with Path(model_file).open("wb") as file:
        pickle.dump(pipeline, file)

    return pipeline


if __name__ == "__main__":
    train_model()
    print(f"Saved trained model to {MODEL_FILE}")
