from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Считываем README.md для long_description
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="nlp_augmentation",
    version="1.0.3",
    author="Дима",
    author_email="email@example.com",
    description="Библиотека для аугментации текстовых данных на нескольких уровнях",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(include=["nlp_augmentation_library", "nlp_augmentation_library.*"]),
    python_requires=">=3.7",
    install_requires=[
  "packaging==21.3",
  "numpy==1.26.4",
  "beautifulsoup4==4.13.4",
  "bs4==0.0.2",
  "cloudpathlib==0.21.1",
  "decorator==5.2.1",
  "emoji==2.14.1",
  "gensim==4.3.3",
  "huggingface-hub==0.31.2",
  "joblib==1.5.0",
  "matplotlib==3.10.3",
  "networkx==3.4.2",
  "nltk==3.9.1",
  "num2words==0.5.14",
  "openpyxl==3.1.5",
  "pandas==2.2.3",
  "pyarrow==20.0.0",
  "scikit-learn==1.6.1",
  "scipy==1.13.1",
  "seaborn==0.13.2",
  "sentencepiece==0.2.0",
  "spacy==3.8.4",
  "text2digits==0.1.0",
  "textblob==0.19.0",
  "textsearch==0.0.24",
  "tokenizers==0.21.1",
  "toml==0.10.2",
  "tqdm==4.67.1",
  "transformers==4.51.3",
  "urllib3==2.4.0",
  "wordcloud==1.9.4",
  "inflect==7.5.0",
  "constituent_treelib==0.0.8",
  "torchvision==0.20.1"
],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    keywords="nlp augmentation text data augmentation machine learning",
    project_urls={
        "Source": "",
        "Tracker": "",
    },
)
