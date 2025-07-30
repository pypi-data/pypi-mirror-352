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