import os
import re
import torch
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

def initialize(content_directory='../content', faiss_index_path='../faiss_index.index'):
    """
    Initializes the FAISS index with vectors extracted from Markdown files.

    Parameters:
        content_directory (str): The directory containing Markdown files.
        faiss_index_path (str): The path to save the FAISS index.

    Returns:
        tuple: A tuple containing the FAISS index and a list of file paths.
    """
    md_data = read_md_files(content_directory)
    vectors = texts_to_vectors(md_data)
    index = initialize_vector_db(vectors)
    # print_retrieved_documents("chatbot", index)
    return index, [os.path.join(content_directory, file) for file in os.listdir(content_directory)]

def read_md_files(directory):
    """
    Reads Markdown files from the specified directory.

    Parameters:
        directory (str): The directory containing Markdown files.

    Returns:
        list: A list of Markdown content from the files.
    """
    loader_md = DirectoryLoader(directory, glob="**/*.md")
    try:
        md_data = loader_md.load()
        print(f"Markdown files loaded successfully: {len(md_data)}")
        return md_data
    except Exception as e:
        print(f"Failed to load markdown files: {e}")
        return []

def texts_to_vectors(md_data):
    """
    Converts Markdown content to vectors.

    Parameters:
        md_data (list): A list of Markdown content.

    Returns:
        list: A list of vectors.
    """
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

def initialize_vector_db(vectors, model_name='sentence-transformers/all-mpnet-base-v2'):
    """
    Initializes the FAISS index with vectors.

    Parameters:
        vectors (list): A list of vectors.
        model_name (str): The name of the Hugging Face model to use for embeddings.

    Returns:
        FAISS: The initialized FAISS index.
    """
    model_kwargs = {"device": "cuda" if torch.cuda.is_available() else "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    hf_embeddings = HuggingFaceEmbeddings(
        model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
    )
    
    vectordb = FAISS.from_documents(documents=vectors, embedding=hf_embeddings)
    return vectordb

def print_retrieved_documents(query, vectordb):
    retriever = vectordb.as_retriever(search_kwargs={"k": 2})
    rdocs = retriever.get_relevant_documents(query)

    for idx, doc in enumerate(rdocs, start=1):
        print(f"Document {idx}:")
        print(f"Source: {doc.metadata.get('source')}\n")
        # Splitting the content into paragraphs for better readability
        paragraphs = doc.page_content.split("\n\n")
        for paragraph in paragraphs:
            print(paragraph)
        print("\n" + "-" * 80 + "\n")  # Add a separator line between documents
