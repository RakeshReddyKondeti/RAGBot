from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from ragbot.readers.data_faq_reader import DataFAQReader
from ragbot.settings import build_settings
from ragbot.storage import build_storage_context, PERSIST_DIR

DATA_DIR = "./data"

def load_documents():
    """Load documents from the input directory using the DataFAQReader for JSON files."""
    print(f"Loading documents from {DATA_DIR}...")

    file_extractor = {
        ".json": DataFAQReader()
    }
    reader = SimpleDirectoryReader(
        input_dir=DATA_DIR,
        file_extractor=file_extractor
    )
    documents = reader.load_data(show_progress=True)
    return documents

def build_index(documents):
    """Build and persist a VectorStoreIndex from the given documents."""
    print("Building index from documents...")
    
    storage_context = build_storage_context()
    index = VectorStoreIndex.from_documents(
        documents=documents,
        storage_context= storage_context,
        show_progress=True
    )
    storage_context.persist()
    return index

def main():
    if PERSIST_DIR.exists():
        import shutil
        print(f"Removing existing persistence directory: {PERSIST_DIR}")
        shutil.rmtree(PERSIST_DIR)

    load_dotenv()
    build_settings()
    documents = load_documents()
    build_index(documents)

if __name__ == "__main__":
    main()