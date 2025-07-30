from gemini_model.model_abstract import Model
from typing_extensions import List, TypedDict
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from ollama import Client

from pydantic import BaseModel, Field

import os
import re


class CitedAnswer(BaseModel):
    """Answer the user question based only on the given sources, and cite the sources used."""

    answer: str = Field(
        ...,
        description="The answer to the user question, which is based only on the given sources.",
    )
    citations: List[int] = Field(
        ...,
        description="The integer IDs of the SPECIFIC sources which justify the answer.",
    )


# Define state for RAG application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: CitedAnswer


class RAG(Model):
    def __init__(self):
        super().__init__()
        """ Model initialization
        """
        self.parameters = {}
        self.output = {}
        self.text_splitter = None

        # Create the connection to the ollama model
        ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.ollama_client = Client(host=ollama_host)

    def readfiles(self, docs_dir, filenames=None):
        text_contents = {}

        # Use provided filenames or list all from directory
        if filenames is None:
            filenames = os.listdir(docs_dir)

        for filename in filenames:
            file_path = os.path.join(docs_dir, filename)

            if not os.path.isfile(file_path):
                continue

            if filename.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                text_contents[filename] = content

            elif filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                content = "\n".join(doc.page_content for doc in documents)
                text_contents[filename] = content

        return text_contents

    def chunksplitter(self, text, chunk_size):
        words = re.findall(r'\S+', text)

        chunks = []
        current_chunk = []
        word_count = 0

        for word in words:
            current_chunk.append(word)
            word_count += 1

            if word_count >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                word_count = 0

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def getembedding(self, chunks: list[str]):
        # Embed all chunks at the same time
        response = self.ollama_client.embed(
            model="nomic-embed-text",
            input=chunks
        )
        embeddings = response.get('embeddings', [])

        if not isinstance(embeddings, list) or len(embeddings) != len(chunks):
            raise ValueError(f"Expected {len(chunks)} embeddings, got {len(embeddings)}")

        return embeddings

    def update_parameters(self, parameters):
        pass

    def initialize_state(self, x):
        pass

    def update_state(self, u, x):
        pass

    def calculate_output(self, u, x):
        pass

    def get_output(self):
        pass
