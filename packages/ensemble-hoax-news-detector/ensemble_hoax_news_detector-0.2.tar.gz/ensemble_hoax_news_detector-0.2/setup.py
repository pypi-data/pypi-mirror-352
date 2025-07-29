from setuptools import setup, find_packages

setup(
    name="ensemble-hoax-news-detector",
    version="0.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "joblib",
        "scikit-learn",
        "lime",
        "numpy",
        "pandas"
    ],
    author="Wayan Surya Adnyana",
    author_email="wayansurya123@gmail.com",
    description="Ensemble Learning Dalam Deteksi Berita Hoax Menggunakan XAI (LIME)",
    url="https://github.com/uyaaaa/ensemble-hoax-news-detector",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)