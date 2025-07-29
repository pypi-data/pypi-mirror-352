from lime.lime_text import LimeTextExplainer
from .model import ensemble_model, tfidf, preprocess_text

# Inisialisasi LIME
explainer = LimeTextExplainer(class_names=["Valid", "Hoax"])

# Fungsi untuk Menjelaskan Prediksi
def explain_prediction(text):
    preprocessed_text = preprocess_text(text)
    tfidf_text = tfidf.transform([preprocessed_text])
    
    # Jalankan LIME
    exp = explainer.explain_instance(
        preprocessed_text,
        lambda x: ensemble_model.predict_proba(tfidf.transform(x)),
        num_features=10
    )
    
    # Prediksi label (0 = Valid, 1 = Hoax)
    proba = ensemble_model.predict_proba(tfidf_text)[0]
    predicted_class = int(proba[1] >= 0.5)
    label_used = predicted_class if predicted_class in exp.local_exp else exp.available_labels()[0]
    
    explanation = {
        "text": text,
        "predicted_label": "Hoax" if predicted_class == 1 else "Valid",
        "probability": {"Valid": float(proba[0]), "Hoax": float(proba[1])},
        "features": [
            {"feature": feat, "weight": float(w), "direction": "↑" if w > 0 else "↓"}
            for feat, w in exp.as_list(label=label_used)
        ],
        "exp_object": exp
    }
    return explanation