# these three lines swap the stdlib sqlite3 lib with the pysqlite3 package
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import pandas as pd
from langchain.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS, Chroma
from langchain.document_loaders import WebBaseLoader
from langchain.document_loaders.merge import MergedDataLoader

class VectorStoreFAISS:
    def __init__(self, csv_file=None ,output_dir="faiss"):
        self.output_dir = output_dir
        self.csv_file = csv_file
        self.documents = []

    def select_topics(self):
        self.df = pd.read_csv(self.csv_file)
        topic = ['LLMmodel', 'RAG', 'Dataset', 'FineTuning', 'Others']
        df = self.df[self.df['collection'].isin(topic)]
        pdf_files = df['path'].tolist()
        urls = df['url'].unique().tolist()

        pdf_files = [pdf_file for pdf_file in pdf_files if pdf_file==pdf_file]
        urls = [url for url in urls if url==url]

        pdf_files = [pdf_file for pdf_file in pdf_files if pdf_file.endswith('.pdf')]
        urls = [url for url in urls if url.startswith('http')]
        return pdf_files, urls

    def get_loader(self):
        pdf_files, urls = self.select_topics()
        for pdf_file in pdf_files:
            loader_pdf = self.get_pdf_loader(pdf_file)
            self.documents.extend(loader_pdf.load())

        loader_web = self.get_web_loader(urls)
        self.documents.extend(loader_web.load())
        # self.loader = MergedDataLoader(loaders=[loader_web, loader_pdf])
        # self.loader = loader_web

    def get_pdf_loader(self, zotero_path=None):
        loader=PyPDFLoader(zotero_path)
        return loader

    def get_web_loader(self, web_links=None):
        loader = WebBaseLoader(web_links)
        return loader

    def get_splitter(self, split_type="TOKEN", chunk_size=1000, chunk_overlap=100):
        if split_type == "CHARACTER":
            self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        elif split_type == "TOKEN":
            self.splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, allowed_special={'<|endoftext|>'})
        else:
            raise NotImplementedError

    def get_embeddings(self):
        # create the embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            # model_name="/data/llm/Llama-2-7b-chat-hf/",
            model_kwargs={'device': 'cpu'})

    def create(self):
        self.get_loader()
        self.get_embeddings()
        self.get_splitter(split_type="CHARACTER", chunk_size=500, chunk_overlap=50)
        texts = self.splitter.split_documents(self.documents)
        # create the vector store database
        db = FAISS.from_documents(texts, self.embeddings)

        # save the vector store
        db.save_local(self.output_dir)
        print(f"Saved vector store to {self.output_dir}")

    def load_vector_store(self):
        self.get_embeddings()
        # load the interpreted information from the local database
        db = FAISS.load_local(self.output_dir, self.embeddings)
        return db

class VectorStoreChromab(VectorStoreFAISS):
    def __init__(self, csv_file=None, output_dir="chromab"):
        super().__init__(csv_file, output_dir)

    def create(self):
        self.get_loader()
        self.get_embeddings()
        self.get_splitter(split_type="CHARACTER", chunk_size=500, chunk_overlap=50)
        # documents = self.loader.load()
        texts = self.splitter.split_documents(self.documents)

        # create the vector store database
        db = Chroma.from_documents(documents=texts, embedding=self.embeddings, persist_directory=self.output_dir)

        print(f"Saved vector store to {self.output_dir}")

    def load_vector_store(self):
        self.get_embeddings()
        # load the interpreted information from the local database
        db = Chroma(persist_directory=self.output_dir, embedding_function=self.embeddings)
        return db

if __name__ == "__main__":
    csv_file = '../zotero.csv'

    vector_store = VectorStoreFAISS(csv_file, output_dir="../vectordb/faiss")
    # vector_store = VectorStoreChromab(csv_file, output_dir="../vectordb/chromab")
    vector_store.create()
