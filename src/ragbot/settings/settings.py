import tiktoken
from llama_index.core.settings import Settings

from ragbot.llms import build_openrouter_llm
from ragbot.embeddings import build_huggingface_embeddings
from ragbot.transformations import build_text_cleaner
from ragbot.node_parsers import build_sentence_splitter

from transformers import AutoTokenizer

def build_settings() -> None:
    Settings.embed_model = build_huggingface_embeddings()
    Settings.llm = build_openrouter_llm()
    Settings.transformations = [
        build_sentence_splitter(),
        build_text_cleaner()
    ]

    # Must set the suitable tokenizer for the LLM
    # Skipping this to avoid adding huggingface api key
    # to add the tokenizer (gated behind a HuggingFace API key)
    # Default tokenizer is tiktoken (gpt models)
    # Settings.tokenizer = tiktoken
