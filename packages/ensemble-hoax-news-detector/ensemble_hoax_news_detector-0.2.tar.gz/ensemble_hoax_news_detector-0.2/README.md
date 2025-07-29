# Ensemble Hoax Detector

Model **Ensemble Learning (Random Forest + AdaBoost)** untuk mendeteksi berita hoax, dengan Explainable AI (LIME).

## 🚀 Instalasi
pip install ensemble-hoax-news-detector
## 🔍 Cara Penggunaan
```python
from ensemble_hoax_news_detector import predict_hoax, explain_prediction

news = "Pemerintah mengumumkan vaksin baru yang diklaim 100% efektif."
result = predict_hoax(news)
print(result)

exp = explain_prediction(news)
exp.show_in_notebook()