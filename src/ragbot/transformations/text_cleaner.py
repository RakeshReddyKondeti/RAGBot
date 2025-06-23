import re
import unicodedata
from typing import Any, Sequence
from llama_index.core.schema import BaseNode
from llama_index.core.schema import TransformComponent


class TextCleaner(TransformComponent):
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any):
        for node in nodes:
            node.text= unicodedata.normalize('NFKD', node.text)

            node.text = node.text.strip()
            node.text = node.text.lower()

            # remove whitespace
            node.text = re.sub(r'\s+', ' ', node.text)

            # can implement stemming or lemmatization here if needed
            # But for now, we will just apply basic cleaning
        
        return nodes


def build_text_cleaner() -> TextCleaner:
    """Build a text cleaner."""
    return TextCleaner()
