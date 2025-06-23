from llama_index.core.node_parser import SentenceSplitter

def build_sentence_splitter() -> SentenceSplitter:
    return SentenceSplitter(
        chunk_size= 512,
        chunk_overlap= 50,
        separator= "\n",
    )