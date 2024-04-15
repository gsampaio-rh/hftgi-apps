import os
import re
import torch
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import MarkdownTextSplitter

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
        print(f"Number of Documents: {len(md_data)}")
        chunks = self.texts_to_vectors(md_data)
        print(f"Number of Chunks: {len(chunks)}")
        self.index = self.initialize_vector_db(chunks)
        self.file_paths = [os.path.join(self.content_directory, file) for file in os.listdir(self.content_directory)]
        return self.index, self.file_paths

    def read_md_files(self):
        loader_md = DirectoryLoader(self.content_directory, glob="**/*.md", show_progress=True, loader_cls=UnstructuredMarkdownLoader)

        try:
            md_data = loader_md.load()
            print(f"Markdown files loaded successfully: {len(md_data)}")
            return md_data
        except Exception as e:
            print(f"Failed to load markdown files: {e}")
            return []

    def texts_to_vectors(self, md_data):
        # recur_splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=1200,
        #     chunk_overlap=60,
        #     separators=["\n\n", "\n", "(?<=\. )", " ", ""],
        #     is_separator_regex=True,
        # )

        # for doc in md_data:
        #     doc.page_content = re.sub("\n{3,}", "\n", doc.page_content)
        #     doc.page_content = re.sub(" {2,}", " ", doc.page_content)

        # md_data_splits = recur_splitter.split_documents(md_data)
        chunks = []
        splitter = MarkdownTextSplitter(chunk_size=512, chunk_overlap=0)
        for chunk in splitter.split_documents(md_data):
            chunks.append(chunk)
        return chunks

    def initialize_vector_db(self, vectors):
        hf_embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name, model_kwargs=self.model_kwargs, encode_kwargs=self.encode_kwargs
        )

        vectordb = FAISS.from_documents(documents=vectors, embedding=hf_embeddings)
        return vectordb

    def retrieve_documents(self, query, k=3, score_threshold=0.1):
        # Retrieve similar chunks based on relevance with metadata
        similar_chunks = self.index.similarity_search_with_relevance_scores(query, k=k, score_threshold=score_threshold)

        # Unpack the tuples to separate page content and scores
        retrieved_text = [chunk[0].page_content for chunk in similar_chunks]
        relevance_scores = [chunk[1] for chunk in similar_chunks]
        sources = [chunk[0].metadata.get('source', 'Unknown source') for chunk in similar_chunks]

        # Create a DataFrame to neatly display the results
        retrieved_chunks = pd.DataFrame({
            "Retrieved Chunks": retrieved_text,
            "Relevance Score": relevance_scores,
            "Source": sources
        })

        # # Optionally, adjust display settings for better readability
        # pd.set_option('display.max_colwidth', None)
        # pd.set_option('display.max_rows', None)

        # Print the DataFrame
        # print(retrieved_chunks)
        return retrieved_chunks

# Example usage
# vectordb_manager = VectorDatabaseManager()
# vectordb_manager.initialize()
# vectordb_manager.print_retrieved_documents("example query")
