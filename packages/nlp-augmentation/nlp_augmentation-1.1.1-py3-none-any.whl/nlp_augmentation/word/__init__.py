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