from pathlib import Path
from llama_index.core.storage import StorageContext
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.graph_stores.simple import SimpleGraphStore
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.vector_stores.simple import NAMESPACE_SEP, DEFAULT_VECTOR_STORE
from llama_index.core.vector_stores.types import (
    DEFAULT_PERSIST_FNAME,
)

PERSIST_DIR = Path("./storage")

def load_or_create_docstore(persist_dir: Path):
    path = persist_dir / "docstore.json"
    if path.exists():
        return SimpleDocumentStore.from_persist_dir(str(persist_dir))
    return SimpleDocumentStore()

def load_or_create_index_store(persist_dir: Path):
    path = persist_dir / "index_store.json"
    if path.exists():
        return SimpleIndexStore.from_persist_dir(str(persist_dir))
    return SimpleIndexStore()

def load_or_create_graph_store(persist_dir: Path):
    path = persist_dir / "graph_store.json"
    if path.exists():
        return SimpleGraphStore.from_persist_dir(str(persist_dir))
    return SimpleGraphStore()

def load_or_create_vector_store(persist_dir: Path):
    # path = persist_dir / DEFAULT_PERSIST_FNAME
    persist_fname = f"{DEFAULT_VECTOR_STORE}{NAMESPACE_SEP}{DEFAULT_PERSIST_FNAME}"
    path = persist_dir / persist_fname
    if path.exists():
        return SimpleVectorStore.from_persist_dir(str(persist_dir))
    return SimpleVectorStore()

def build_storage_context(persist_dir: Path = PERSIST_DIR):
    persist_dir.mkdir(parents=True, exist_ok=True)
    docstore = load_or_create_docstore(persist_dir)
    index_store = load_or_create_index_store(persist_dir)
    graph_store = load_or_create_graph_store(persist_dir)
    vector_store = load_or_create_vector_store(persist_dir)
    return StorageContext.from_defaults(
        docstore=docstore,
        index_store=index_store,
        graph_store=graph_store,
        vector_store=vector_store,
        persist_dir=str(persist_dir),
    )

# Usage:
# storage_context = build_storage_context()