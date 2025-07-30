import logging
import random
from typing import Optional, List, Tuple
# Отключаем использование GPU для трансформеров, чтобы избежать CUDA-ошибок
# os.environ["CUDA_VISIBLE_DEVICES"] = ""

import nltk
from nltk.tree import Tree
from constituent_treelib import ConstituentTree, Language
from nlp_augmentation.utils.text_ops import tokenize
from nlp_augmentation.utils.lazy import (
    get_pipe_parrot,
    get_pipe_bart_sum,
    get_bart_tokenizer,
    get_pipe_back_en2fr,
    get_pipe_back_fr2en,
    get_pipe_back_en2es,
    get_pipe_back_es2en,
)
from transformers import logging as transformers_logging

# Отключаем логи Transformers и NLTK
transformers_logging.set_verbosity_error()
logging.getLogger("nltk").setLevel(logging.ERROR)

# Глобальный конвейер для парсинга синтаксических деревьев
_CONS = ConstituentTree.create_pipeline(
    Language.English, ConstituentTree.SpacyModelSize.Medium
)

def chunk_sentences(text: str, chunk_size: int = 4) -> List[str]:
    """
    Разбивает текст на фрагменты по chunk_size предложений.
    """
    sents = nltk.sent_tokenize(text)
    return [" ".join(sents[i:i+chunk_size]) for i in range(0, len(sents), chunk_size)]

def _chunks_by_bpe(texts: List[str], tokenizer, limit: int) -> List[str]:
    chunks, buf, cur = [], [], 0
    for t in texts:
        ln = len(tokenizer(t)["input_ids"])
        if ln > limit:
            if buf:
                chunks.append(" ".join(buf))
                buf, cur = [], 0
            chunks.append(t)
            continue
        if cur + ln > limit - 2:
            chunks.append(" ".join(buf))
            buf, cur = [], 0
        buf.append(t)
        cur += ln
    if buf:
        chunks.append(" ".join(buf))
    return chunks

class TextAugmentor:
    def __init__(
        self,
        seed: Optional[int] = None,
        chunk_size: int = 4,
        device: int = -1
    ) -> None:
        """
        :param seed: сид для RNG
        :param chunk_size: сколько предложений в одном куске
        :param device: индекс GPU или -1 для CPU
        """
        self.rng = random.Random(seed)
        nltk.download("punkt", quiet=True)
        self.chunk_size = chunk_size

        # Передаём явно параметр device, чтобы всегда использовать CPU
        device_arg = {"device": device}

        # Heavy pipelines one-time init
        self.parrot         = get_pipe_parrot(**device_arg)
        self.summarizer     = get_pipe_bart_sum(**device_arg)
        self.bart_tokenizer = get_bart_tokenizer()

        self.bt_en2fr = get_pipe_back_en2fr(**device_arg)
        self.bt_fr2en = get_pipe_back_fr2en(**device_arg)
        self.bt_en2es = get_pipe_back_en2es(**device_arg)
        self.bt_es2en = get_pipe_back_es2en(**device_arg)

    def shuffle(self, text: str) -> str:
        sents = nltk.sent_tokenize(text)
        self.rng.shuffle(sents)
        return " ".join(sents)

    def shuffle_subtrees(self, text: str, label: str = "JJ", p: float = 1.0) -> str:
        out = []
        for chunk in chunk_sentences(text, self.chunk_size):
            try:
                for sent in _CONS(chunk).sents:
                    tree = ConstituentTree(sent.text, _CONS)
                    if self.rng.random() < p:
                        self._rec_shuffle(tree.nltk_tree, label)
                    out.append(" ".join(tree.nltk_tree.leaves()))
            except ValueError:
                out.append(chunk)
        return " ".join(out)

    def _rec_shuffle(self, node: Tree, label: str) -> None:
        idxs = [i for i, ch in enumerate(node)
                if isinstance(ch, Tree) and ch.label() == label]
        if len(idxs) > 1:
            vals = [node[i] for i in idxs]
            self.rng.shuffle(vals)
            for pos, new in zip(idxs, vals):
                node[pos] = new
        for ch in node:
            if isinstance(ch, Tree):
                self._rec_shuffle(ch, label)

    def delete_subtree(self, text: str, label: str = "PP", p: float = 1.0) -> str:
        out = []
        for chunk in chunk_sentences(text, self.chunk_size):
            try:
                for sent in _CONS(chunk).sents:
                    tree = ConstituentTree(sent.text, _CONS)
                    if self.rng.random() < p:
                        self._rec_delete(tree.nltk_tree, label)
                    out.append(" ".join(tree.nltk_tree.leaves()))
            except ValueError:
                out.append(chunk)
        return " ".join(out)

    def _rec_delete(self, node: Tree, label: str) -> None:
        candidates = []
        def collect(n: Tree):
            for i, ch in enumerate(n):
                if isinstance(ch, Tree):
                    if ch.label() == label:
                        candidates.append((n, i))
                    collect(ch)
        collect(node)
        if candidates:
            parent, idx = self.rng.choice(candidates)
            del parent[idx]

    def split_sbar(self, text: str, p: float = 1.0) -> str:
        out = []
        for chunk in chunk_sentences(text, self.chunk_size):
            try:
                for sent in _CONS(chunk).sents:
                    tree = ConstituentTree(sent.text, _CONS)
                    if self.rng.random() < p:
                        root = tree.nltk_tree
                        sbar_nodes = [
                            (i, ch) for i, ch in enumerate(root)
                            if isinstance(ch, Tree) and ch.label() == "SBAR"
                        ]
                        if sbar_nodes:
                            idx, sbar = self.rng.choice(sbar_nodes)
                            main = Tree(root.label(), root[:idx] + root[idx+1:])
                            clause = next(
                                (c for c in sbar if isinstance(c, Tree) and c.label() == "S"),
                                None
                            )
                            if clause:
                                out.append(" ".join(main.leaves()))
                                out.append(" ".join(clause.leaves()))
                                continue
                    out.append(" ".join(tree.nltk_tree.leaves()))
            except ValueError:
                out.append(chunk)
        return " ".join(out)

    def back_translate(
            self,
            text: str,
            max_len: int = 256,
            batch_size: int = 8
    ) -> str:
        engines = [
            (self.bt_en2fr, self.bt_fr2en),
            (self.bt_en2es, self.bt_es2en),
        ]
        frags_by_engine = {0: [], 1: []}

        # 1. Собираем куски по движкам
        for chunk in chunk_sentences(text, self.chunk_size):
            for sent in nltk.sent_tokenize(chunk):
                idx = self.rng.choice([0, 1])
                en2xx, xx2en = engines[idx]
                toks = en2xx.tokenizer(sent)["input_ids"]
                pieces = (
                    [sent]
                    if len(toks) <= max_len
                    else _chunks_by_bpe([sent], en2xx.tokenizer, max_len)
                )
                frags_by_engine[idx].extend(pieces)

        out = []
        # 2. Пакетно переводим и обратно
        for idx, pieces in frags_by_engine.items():
            if not pieces:
                continue
            en2xx, xx2en = engines[idx]

            # прямой перевод
            raw_fwd = en2xx(pieces, max_length=max_len, batch_size=batch_size)
            mids = []
            for item in raw_fwd:
                # item может быть dict или список dict
                if isinstance(item, list):
                    mids.extend([sub["translation_text"] for sub in item])
                else:
                    mids.append(item["translation_text"])

            # обратный перевод
            raw_back = xx2en(mids, max_length=max_len, batch_size=batch_size)
            for item in raw_back:
                if isinstance(item, list):
                    out.extend([sub["translation_text"] for sub in item])
                else:
                    out.append(item["translation_text"])

        return " ".join(out)

    def paraphrase(
            self,
            text: str,
            top_k: int = 3,
            max_tok: int = 128,
            batch_size: int = 8,
            temperature: float = 1.2
    ) -> str:
        tok = self.parrot.tokenizer
        segs: List[str] = []
        for chunk in chunk_sentences(text, self.chunk_size):
            for sent in nltk.sent_tokenize(chunk):
                ids = tok(sent)["input_ids"]
                if len(ids) > max_tok:
                    segs.extend(_chunks_by_bpe([sent], tok, max_tok))
                else:
                    segs.append(sent)

        if not segs:
            return text

        # 1) Запускаем пакетную генерацию
        raw = self.parrot(
            segs,
            num_return_sequences=top_k,
            num_beams=max(top_k, 3),
            do_sample=True,
            temperature=temperature,
            batch_size=batch_size
        )

        # 2) Выровняем в плоский список кандидатов
        flat = []
        for item in raw:
            if isinstance(item, list):
                flat.extend(item)
            else:
                flat.append(item)

        # 3) Разбиваем на блоки по top_k
        out: List[str] = []
        for i in range(len(segs)):
            block = flat[i * top_k:(i + 1) * top_k]
            if not block:
                continue
            cand = self.rng.choice(block)
            # 4) Извлекаем строку везде, где это возможно
            if isinstance(cand, dict):
                text_gen = cand.get("generated_text") or next(iter(cand.values()))
            elif isinstance(cand, str):
                text_gen = cand
            else:
                text_gen = str(cand)
            out.append(text_gen.strip())

        return " ".join(out)

    def hierarchical_summarize(
        self,
        text: str,
        max_chunk_tokens: int = 1024,
        max_length: int = 50,
        min_length: int = 20,
        do_sample: bool = False
    ) -> str:
        tok = self.bart_tokenizer
        out_text = text
        for _ in range(5):
            ids = tok.encode(out_text, add_special_tokens=False)
            if len(ids) <= max_chunk_tokens:
                break
            parts = _chunks_by_bpe(nltk.sent_tokenize(out_text), tok, max_chunk_tokens)
            summarized = []
            for part in parts:
                try:
                    summarized.append(
                        self.summarizer(
                            part,
                            max_length=min(max_length, len(tok.encode(part)) - 1),
                            min_length=min(min_length, (len(tok.encode(part)) + 1) // 2),
                            do_sample=do_sample
                        )[0]["summary_text"].strip()
                    )
                except Exception:
                    summarized.append(part)
            out_text = " ".join(summarized)
        try:
            return self.summarizer(
                out_text,
                max_length=min(max_length, len(tok.encode(out_text)) - 1),
                min_length=min_length,
                do_sample=do_sample
            )[0]["summary_text"]
        except Exception:
            return text

    def n_chunk_crossover(
        self,
        text_a: str,
        text_b: str,
        n_chunks: int
    ) -> str:
        sents_a = nltk.sent_tokenize(text_a)
        sents_b = nltk.sent_tokenize(text_b)
        L_a, L_b = len(sents_a), len(sents_b)
        def _split_chunks(sents: List[str], L: int) -> List[List[str]]:
            bounds = [int(i * L / n_chunks) for i in range(n_chunks + 1)]
            return [sents[bounds[i]:bounds[i+1]] for i in range(n_chunks)]
        chunks_a = _split_chunks(sents_a, L_a)
        chunks_b = _split_chunks(sents_b, L_b)
        a_first = self.rng.choice([True, False])
        child: List[str] = []
        for i in range(n_chunks):
            if a_first:
                child += chunks_a[i] + chunks_b[i]
            else:
                child += chunks_b[i] + chunks_a[i]
        return " ".join(child)
