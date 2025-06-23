import json
from typing import List
from llama_index.core import Document
from llama_index.core.schema import MediaResource
from llama_index.core.readers.base import BaseReader


def is_json_file(file_path: str) -> bool:
    """Check if the given file is a JSON file by extension."""
    return isinstance(file_path, str) and file_path.lower().endswith('.json')

def load_json(file_path: str):
    """Load and return data from a JSON file."""
    if not is_json_file(file_path):
        raise ValueError("Provided file is not a JSON file.")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load JSON file: {e}")

class DataFAQReader(BaseReader):
    def load_data(self, file, extra_info = None):
        documents = []
        data = load_json(str(file))
        extra_info = extra_info or {}

        for item in data:
            questions = item.get("questions", [])
            answer = item.get("answer", "")
            doc_info = {
                **extra_info,
                "answer": answer,
            }
            
            for question in questions:
                documents.append(
                    Document(
                        text_resource = MediaResource(text=question),
                        extra_info=doc_info
                    )
                )
        
        return documents

