import os
from llama_index.llms.openrouter import OpenRouter
from transformers import AutoTokenizer


def build_openrouter_llm() -> OpenRouter:
    api_key = os.getenv("OPENROUTER_API_KEY")

    model = "meta-llama/llama-3.2-3b-instruct"

    llm = OpenRouter(
        model = model,
        max_tokens= 1000,
        temperature= 0.1,
        context_window= 4096,
        api_key= api_key,
    )

    # tokenizer = AutoTokenizer.from_pretrained(
    #     model,
    #     cache_dir="./models",
    # )
    return llm