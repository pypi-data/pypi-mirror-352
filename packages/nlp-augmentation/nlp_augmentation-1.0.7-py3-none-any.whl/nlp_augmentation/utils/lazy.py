import functools
import os
import torch
import spacy
from transformers import pipeline, AutoTokenizer
import gensim.downloader as api

# Всегда по умолчанию использовать CPU, если не передан явный device>=0
DEFAULT_DEVICE = -1

@functools.lru_cache(maxsize=1)
def get_nlp():
    return spacy.load("en_core_web_sm", exclude=["ner", "parser", "lemmatizer"])

@functools.lru_cache(maxsize=1)
def get_fill_mask(
    model: str = "roberta-base",
    device: int = DEFAULT_DEVICE
):
    return pipeline(
        "fill-mask",
        model=model,
        device=device
    )

@functools.lru_cache(maxsize=1)
def get_glove(
    name: str = "glove-wiki-gigaword-100"
):
    return api.load(name)

# Parrot (T5 paraphraser)
@functools.lru_cache(maxsize=1)
def get_pipe_parrot(
    device: int = DEFAULT_DEVICE
):
    return pipeline(
        "text2text-generation",
        model="prithivida/parrot_paraphraser_on_T5",
        device=device
    )

# BART summarizer
@functools.lru_cache(maxsize=1)
def get_pipe_bart_sum(
    device: int = DEFAULT_DEVICE
):
    return pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device=device
    )

@functools.lru_cache(maxsize=1)
def get_bart_tokenizer():
    return AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

# Back-translation (FR, ES)
@functools.lru_cache(maxsize=1)
def get_pipe_back_en2fr(
    device: int = DEFAULT_DEVICE
):
    return pipeline(
        "translation_en_to_fr",
        model="Helsinki-NLP/opus-mt-en-fr",
        device=device
    )

@functools.lru_cache(maxsize=1)
def get_pipe_back_fr2en(
    device: int = DEFAULT_DEVICE
):
    return pipeline(
        "translation_fr_to_en",
        model="Helsinki-NLP/opus-mt-fr-en",
        device=device
    )

@functools.lru_cache(maxsize=1)
def get_pipe_back_en2es(
    device: int = DEFAULT_DEVICE
):
    return pipeline(
        "translation_en_to_es",
        model="Helsinki-NLP/opus-mt-en-es",
        device=device
    )

@functools.lru_cache(maxsize=1)
def get_pipe_back_es2en(
    device: int = DEFAULT_DEVICE
):
    return pipeline(
        "translation_es_to_en",
        model="Helsinki-NLP/opus-mt-es-en",
        device=device
    )
