# word/augmentor.py

import random
from typing import List, Optional

import inflect
import nltk
from nltk.corpus import stopwords, wordnet as wn
from num2words import num2words
from text2digits import text2digits

from nlp_augmentation.utils.lazy import get_nlp, get_fill_mask, get_glove
from nlp_augmentation.utils.text_ops import tokenize, detokenize
from nlp_augmentation.utils.resources import load_slang_csv
from decimal import InvalidOperation

_STOP_SET = set(stopwords.words("english"))
_INFLECT = inflect.engine()
_T2D = text2digits.Text2Digits()

class WordAugmentor:
    """
    Аугментация на уровне слов.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self._glove = None

    def _check_p(self, p: float):
        if not 0.0 <= p <= 1.0:
            raise ValueError("p must be in [0, 1]")

    def delete(self, text: str, p: float = 0.05) -> str:
        self._check_p(p)
        toks = tokenize(text)
        kept = [t for t in toks if not t.isalnum() or self._rng.random() > p]
        return detokenize(kept)

    def insert(self, text: str, p: float = 0.05, pool: Optional[List[str]] = None) -> str:
        self._check_p(p)
        pool = pool or list(_STOP_SET)
        out: List[str] = []
        for t in tokenize(text):
            if t.isalnum() and self._rng.random() < p:
                out.append(self._rng.choice(pool))
            out.append(t)
        return detokenize(out)

    def swap(self, text: str, p: float = 0.05) -> str:
        self._check_p(p)
        toks = tokenize(text)
        i = 0
        while i < len(toks) - 1:
            if toks[i].isalpha() and toks[i+1].isalpha() and self._rng.random() < p:
                toks[i], toks[i+1] = toks[i+1], toks[i]
                i += 2
            else:
                i += 1
        return detokenize(toks)

    def synonym(self, text: str, p: float = 0.05) -> str:
        self._check_p(p)
        toks = tokenize(text)
        for i, t in enumerate(toks):
            lw = t.lower()
            if t.isalpha() and lw not in _STOP_SET and self._rng.random() < p:
                syns = {
                    lemma.replace("_", " ")
                    for syn in wn.synsets(t)
                    for lemma in syn.lemma_names()
                    if lemma.lower() != lw
                }
                if syns:
                    toks[i] = self._rng.choice(list(syns))
        return detokenize(toks)

    def embedding(self, text: str, p: float = 0.1, k: int = 5) -> str:
        self._check_p(p)
        if self._glove is None:
            self._glove = get_glove()
        toks = tokenize(text)
        for i, t in enumerate(toks):
            lw = t.lower()
            if (t.isalpha() and lw in self._glove.key_to_index
                    and lw not in _STOP_SET and self._rng.random() < p):
                neigh = [w for w, _ in self._glove.most_similar(lw, topn=k+10) if w != lw][:k]
                if neigh:
                    toks[i] = self._rng.choice(neigh)
        return detokenize(toks)

    def contextual(self, text: str, p: float = 0.1, top_k: int = 5, window: int = 128) -> str:
        """
        Замена слов в контексте с помощью маскированной языковой модели (MLM).
        """
        self._check_p(p)
        toks = tokenize(text)
        fill = get_fill_mask()
        mask = fill.tokenizer.mask_token

        # Индексы токенов для замены
        idxs = [
            i for i, t in enumerate(toks)
            if t.isalpha() and t.lower() not in _STOP_SET and self._rng.random() < p
        ]
        if not idxs:
            return text

        for i in idxs:
            # Формируем маскированное предложение с окном
            masked = " ".join(toks[max(0, i - window):i] + [mask] + toks[i + 1:i + 1 + window])
            try:
                result = fill(masked, top_k=top_k)
                if isinstance(result, list):
                    candidates = [
                        r["token_str"].strip()
                        for r in result if isinstance(r, dict) and r.get("token_str", "").isalpha()
                    ]
                    if candidates:
                        toks[i] = self._rng.choice(candidates)
            except Exception:
                continue  # Пропускаем, если модель не вернула ничего или произошла ошибка

        return detokenize(toks)

    def morph(self, text: str, p: float = 0.1, plural_only: bool = False) -> str:
        self._check_p(p)
        doc = get_nlp()(text)
        out = []
        for tok in doc:
            if tok.is_alpha and tok.lower_ not in _STOP_SET and self._rng.random() < p:
                if tok.pos_ == "NOUN":
                    if tok.tag_ == "NN":
                        out.append(_INFLECT.plural(tok.text))
                    elif tok.tag_ == "NNS":
                        out.append(_INFLECT.singular_noun(tok.text) or tok.text)
                    else:
                        out.append(tok.text)
                elif tok.pos_ == "VERB" and not plural_only:
                    if tok.tag_ in {"VB", "VBP", "VBZ"}:
                        out.append(tok.text + "ing")
                    elif tok.tag_ in {"VBD", "VBN"}:
                        out.append(tok.text + ("d" if tok.text.endswith("e") else "ed"))
                    else:
                        out.append(tok.text)
                else:
                    out.append(tok.text)
            else:
                out.append(tok.text)
        return detokenize(out)

    def abbreviations(self, text: str, p: float = 0.8) -> str:
        self._check_p(p)
        s2l, l2s = load_slang_csv()
        mapping = {**s2l, **l2s}
        toks, out, i = tokenize(text), [], 0
        while i < len(toks):
            lw = toks[i].lower()
            if lw in _STOP_SET:
                out.append(toks[i])
                i += 1
                continue
            replaced = False
            for span in range(5, 0, -1):
                phrase = " ".join(toks[i:i+span]).lower()
                if phrase in mapping and self._rng.random() < p:
                    out.append(mapping[phrase])
                    i += span
                    replaced = True
                    break
            if not replaced:
                out.append(toks[i])
                i += 1
        return detokenize(out)

    def digits_to_words(self, text: str) -> str:
        return nltk.re.compile(r"\b\d+\b").sub(lambda m: num2words(int(m.group()), lang="en"), text)

    def words_to_digits(self, text: str) -> str:
        try:
            return _T2D.convert(text)
        except InvalidOperation:
            return text
