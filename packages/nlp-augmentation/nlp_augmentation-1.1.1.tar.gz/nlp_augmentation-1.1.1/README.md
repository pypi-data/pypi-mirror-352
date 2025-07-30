# nlp_augmentation

Библиотека для аугментации текстовых данных на нескольких уровнях — от символов и слов до синтаксиса и генеративных моделей.

---

## Возможности

- **CharAugmentor** — аугментация на уровне символов: удаление, вставка, замена, перестановка, изменение регистра.
- **WordAugmentor** — аугментация на уровне слов: удаление, вставка, синонимы, контекстная замена, морфологические преобразования, аббревиатуры, преобразование чисел.
- **TextAugmentor** — синтаксическая аугментация: перестановка предложений, удаление поддеревьев, парафраз, суммаризация, обратный перевод, crossover.
- **Generator** — генеративные методы на базе предобученных моделей Hugging Face.

---

## Установка
```bash
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
nltk.download("stopwords")
nltk.download('wordnet')
nltk.download('punkt_tab')
pip install nlp_augmentation