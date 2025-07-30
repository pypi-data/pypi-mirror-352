# nlp_augmentation_library

**nlp_augmentation_library** — это современная библиотека для аугментации текстовых данных на нескольких уровнях: символном, словесном, синтаксическом и генеративном. Она предназначена для повышения качества моделей обработки естественного языка (NLP) путем расширения объема и разнообразия обучающих данных.

---

## Возможности

- **CharAugmentor** — аугментация на уровне символов: удаление, вставка, замена, перестановка, изменение регистра.
- **WordAugmentor** — аугментация на уровне слов: удаление, вставка, синонимы, контекстная замена, морфологические преобразования, аббревиатуры, преобразование чисел.
- **TextAugmentor** — синтаксическая аугментация: перестановка предложений, удаление поддеревьев, парафраз, суммаризация, обратный перевод, crossover.
- **Generator** — генеративные методы на базе предобученных моделей Hugging Face.

---

## Установка

Рекомендуется использовать Python версии 3.7 и выше.

```bash
pip install nlp_augmentation_library

pip install git+https://github.com/PrithivirajDamodaran/Parrot_Paraphraser.git
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121
