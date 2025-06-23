import torch
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def build_huggingface_embeddings() -> HuggingFaceEmbedding:

    embed_model = HuggingFaceEmbedding(
        model_name = "intfloat/multilingual-e5-large-instruct",
        device="cuda" if torch.cuda.is_available() else "cpu",
        cache_folder= "./models"
    )

    return embed_model