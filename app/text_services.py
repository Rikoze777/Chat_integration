import re
from tokenizers import Tokenizer
from vertexai.preview import tokenization
from vertexai.tokenization._tokenizers import PreviewTokenizer
from tokenizers import Tokenizer


downloaded_tokenizers = {
    "gemini": tokenization.get_tokenizer_for_model("gemini-1.5-flash-001"),
    "llama-3.1": Tokenizer.from_pretrained("Xenova/Meta-Llama-3.1-Tokenizer"),
    "llama-3.2": Tokenizer.from_pretrained("pcuenq/Llama-3.2-1B-Instruct-tokenizer"),
    "zephyr": Tokenizer.from_pretrained("HuggingFaceH4/zephyr-7b-beta"),
    "grok-1": Tokenizer.from_pretrained("Xenova/grok-1-tokenizer"),
    "gpt-4": Tokenizer.from_pretrained("Xenova/gpt-4"),
    "gpt-4o": Tokenizer.from_pretrained("Xenova/gpt-4o"),
    "gpt-3.5-turbo": Tokenizer.from_pretrained("Xenova/gpt-3.5-turbo"),
    "deepseek-2.5": Tokenizer.from_pretrained("deepseek-ai/DeepSeek-V2.5"),
}

DEFAULT_TOKENIZER = downloaded_tokenizers["gemini"]


def clean_text(raw_text):
    """
    Очистка текста от ненужной информации и извлечение ключевых данных.
    """

    clean = re.sub(r"\[.*?\]\(.*?\)", "", raw_text)  # Убираем ссылки
    clean = re.sub(r"\n\s*\n", "\n", clean)  # Убираем лишние пустые строки
    clean = clean.replace("\\", "") # удаляем \
    text = clean.strip()

    return text


def encode_text(
    text: str,
    tokenizer: PreviewTokenizer | Tokenizer = DEFAULT_TOKENIZER,
):
    if isinstance(tokenizer, Tokenizer):  # HF
        encoded = tokenizer.encode(text)
        ids, tokens = encoded.ids, encoded.tokens

    elif isinstance(tokenizer, PreviewTokenizer):  # Gemini
        encoded = tokenizer.compute_tokens(text)
        ids, tokens = (
            encoded.tokens_info[0].token_ids,
            encoded.tokens_info[0].tokens
        )

    return {
        "ids": ids,
        "tokens": tokens,
    }


def count_tokens(
    text: str,
    tokenizer: PreviewTokenizer | Tokenizer = DEFAULT_TOKENIZER,
):
    if isinstance(tokenizer, Tokenizer):  # HF
        encoded = encode_text(text, tokenizer=tokenizer)
        return len(encoded["ids"])
    elif isinstance(tokenizer, PreviewTokenizer):  # Gemini
        result = tokenizer.count_tokens(text)
        return result.total_tokens