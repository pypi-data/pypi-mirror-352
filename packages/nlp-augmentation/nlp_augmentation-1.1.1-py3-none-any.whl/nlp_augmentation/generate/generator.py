# generate/generator.py

import torch
import random
from transformers import pipeline
from typing import Optional, List, Dict, Any


_GENERATOR_CACHE: Dict[str, Any] = {}


def _get_text_generator(model_name: str, device: int):
    key = f"{model_name}:{device}"
    if key not in _GENERATOR_CACHE:
        gen = pipeline(
            "text-generation",
            model=model_name,
            trust_remote_code=True,
            device=device,
        )
        # ensure EOS and PAD tokens are set for proper stopping
        gen.tokenizer.pad_token = gen.tokenizer.eos_token
        gen.model.config.pad_token_id = gen.tokenizer.eos_token_id
        gen.model.config.eos_token_id = gen.tokenizer.eos_token_id
        gen.model.config.early_stopping = True
        _GENERATOR_CACHE[key] = gen
    return _GENERATOR_CACHE[key]

def _truncate_at_end(text: str) -> str:
    """
    Truncate the generated text at the last sentence-ending punctuation to avoid abrupt cuts.
    """
    # find last occurrence of sentence terminator
    idx = max(text.rfind(p) for p in ('.', '!', '?'))
    if idx != -1:
        return text[:idx+1]
    return text

def Generator(
    prompt: str,
    model_name: str = "microsoft/phi-2",
    num_texts: int = 5,
    max_new_tokens: int = 100,
    temperature: float = 1.2,
    top_p: float = 0.9,
    repetition_penalty: float = 1.2,
    device: Optional[int] = None,
    seed: Optional[int] = None,
) -> List[str]:
    """
    Generate text continuations with clear end-of-text signals.
    """
    if device is None:
        device = 0 if torch.cuda.is_available() else -1

    generator = _get_text_generator(model_name, device)

    if seed is not None:
        torch.manual_seed(seed)
        random.seed(seed)

    tokenizer = generator.tokenizer
    # compute max_length for generation
    prompt_tokens = tokenizer(prompt, return_tensors="pt").input_ids
    prompt_len = prompt_tokens.shape[-1]
    max_length = prompt_len + max_new_tokens

    results = generator(
        prompt,
        max_length=max_length,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=temperature,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
        num_return_sequences=num_texts,
        return_full_text=False,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )

    # post-process to avoid abrupt ending
    generated: List[str] = []
    for item in results:
        text = item.get("generated_text", "").strip()
        # truncate at last sentence-ending punctuation
        text = _truncate_at_end(text)
        generated.append(text)

    return generated
