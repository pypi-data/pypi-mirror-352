from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Считываем README.md для long_description
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="nlp_augmentation_library",
    version="1.0.0",
    author="Дима",
    author_email="email@example.com",
    description="Библиотека для аугментации текстовых данных на нескольких уровнях",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(include=["nlp_augmentation_library", "nlp_augmentation_library.*"]),
    python_requires=">=3.7",
    install_requires=[
        "nltk>=3.9.1",
        "inflect>=7.5.0",
        "num2words>=0.5.14",
        "text2digits>=0.1.0",
        "spacy>=3.8.4",
        "torch>=2.5.1",
        "transformers>=4.51.3",
        "constituent_treelib>=0.0.8",

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
