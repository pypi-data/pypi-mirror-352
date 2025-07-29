import joblib
import re
import os

# Load model dan vectorizer dari folder assets
base_path = os.path.dirname(__file__)
ensemble_model = joblib.load(os.path.join(base_path, "assets/ensemble_model.joblib"))
tfidf = joblib.load(os.path.join(base_path, "assets/tfidf_vectorizer.joblib"))

# Fungsi Preprocessing Teks
def preprocess_text(text):
    text = re.sub(r"http\S+", "", text)  # Hapus URL
    text = re.sub(r"[^a-zA-Z ]", "", text)  # Hapus karakter non-alfabet
    text = text.lower()  # Konversi ke huruf kecil
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Fungsi Prediksi
def predict_hoax(text: str) -> dict:
    preprocessed_text = preprocess_text(text)
    tfidf_text = tfidf.transform([preprocessed_text])
    
    prediction = ensemble_model.predict(tfidf_text)[0]
    probability = ensemble_model.predict_proba(tfidf_text)[0]
    
    return {
        "text": text,
        "label": "Valid" if prediction == 0 else "Hoax",
        "probability": {"Valid": float(probability[0]), "Hoax": float(probability[1])}
    }