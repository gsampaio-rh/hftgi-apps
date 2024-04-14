import os
import re
import torch
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

class VectorDatabaseManager:
    def __init__(self, content_directory='../content', model_name='sentence-transformers/all-mpnet-base-v2'):
        self.content_directory = content_directory
        self.model_name = model_name
        self.model_kwargs = {"device": "cuda" if torch.cuda.is_available() else "cpu"}
        self.encode_kwargs = {"normalize_embeddings": False}
        self.index = None
        self.file_paths = []

    def initialize(self):
        md_data = self.read_md_files()
        vectors = self.texts_to_vectors(md_data)
        self.index = self.initialize_vector_db(vectors)
        self.file_paths = [os.path.join(self.content_directory, file) for file in os.listdir(self.content_directory)]
        return self.index, self.file_paths

    def read_md_files(self):
        loader_md = DirectoryLoader(self.content_directory, glob="**/*.md")
        try:
            md_data = loader_md.load()
            print(f"Markdown files loaded successfully: {len(md_data)}")
            return md_data
        except Exception as e:
            print(f"Failed to load markdown files: {e}")
            return []

    def texts_to_vectors(self, md_data):
        recur_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=60,
            separators=["\n\n", "\n", "(?<=\. )", " ", ""],
            is_separator_regex=True,
        )

        for doc in md_data:
            doc.page_content = re.sub("\n{3,}", "\n", doc.page_content)
            doc.page_content = re.sub(" {2,}", " ", doc.page_content)

        md_data_splits = recur_splitter.split_documents(md_data)
        return md_data_splits

    def initialize_vector_db(self, vectors):
        hf_embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name, model_kwargs=self.model_kwargs, encode_kwargs=self.encode_kwargs
        )
        vectordb = FAISS.from_documents(documents=vectors, embedding=hf_embeddings)
        return vectordb

    def print_retrieved_documents(self, query):
        retriever = self.index.as_retriever(search_kwargs={"k": 2})
        rdocs = retriever.get_relevant_documents(query)

        for idx, doc in enumerate(rdocs, start=1):
            print(f"Document {idx}:")
            print(f"Source: {doc.metadata.get('source')}\n")
            paragraphs = doc.page_content.split("\n\n")
            for paragraph in paragraphs:
                print(paragraph)
            print("\n" + "-" * 80 + "\n")

# Example usage
# vectordb_manager = VectorDatabaseManager()
# vectordb_manager.initialize()
# vectordb_manager.print_retrieved_documents("example query")
