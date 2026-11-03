from pathlib import Path

import joblib
from lime.lime_text import LimeTextExplainer

# Load the model files from this folder
BASE_DIR = Path(__file__).resolve().parent
model = joblib.load(BASE_DIR / "model.pkl")
vectorizer = joblib.load(BASE_DIR / "vectorizer.pkl")

# IMPORTANT: Verify these labels against the training code.
LABEL_NAMES = {
    0: "Likely Fake",
    1: "Likely Real",
}

# Match the labels to the model's actual class order
class_names = [
    LABEL_NAMES.get(int(label), str(label))
    for label in model.classes_
]

explainer = LimeTextExplainer(class_names=class_names)


def predict_probabilities(texts):
    """Convert articles to TF-IDF and return model probabilities."""
    text_vectors = vectorizer.transform(texts)
    return model.predict_proba(text_vectors)


def get_explanation(sample_text, num_features=8):
    """Explain the model's prediction for an article."""
    if not isinstance(sample_text, str) or not sample_text.strip():
        raise ValueError("Please enter article text.")

    return explainer.explain_instance(
        text_instance=sample_text.strip(),
        classifier_fn=predict_probabilities,
        labels=tuple(range(len(model.classes_))),
        num_features=num_features,
    )


if __name__ == "__main__":
    article = (
        "The government announced a new public transport policy today."
    )

    probabilities = predict_probabilities([article])[0]
    predicted_index = int(probabilities.argmax())
    predicted_class = model.classes_[predicted_index]

    print("Model classes:", list(model.classes_))
    print("Prediction:", LABEL_NAMES.get(
        int(predicted_class), str(predicted_class)
    ))

    explanation = get_explanation(article)

    print("\nWords influencing the prediction:")
    for word, weight in explanation.as_list(label=predicted_index):
        print(f"{word}: {weight:+.4f}")