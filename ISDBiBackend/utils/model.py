# ISDBiBackend/utils/model.py
from langchain_huggingface import HuggingFaceEmbeddings  
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_together import ChatTogether
import os
from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain.schema import Document

class LLMHandler : 
    def __init__ (self , model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free" , 
                  chunk_size = 500 , 
                  chunk_overlap = 100 ) :
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.pdf_path = []
        self.documents = []
        self.chain = ""
        self.db = ""
        self.template = "" 
        self.retriever = ""
    

    def load_specific_documents(self, pdf_path):
        chunks = []
        splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        for path in pdf_path:
            loader = PyPDFLoader(path)
            document = loader.load()
            # Add file name as metadata
            for doc in document:
                doc.metadata["source"] = os.path.basename(path)
                print (doc.metadata["source"])
            self.documents.append(document)
            chunks += splitter.split_documents(document)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        db = Chroma.from_documents(chunks, embedding=embeddings, persist_directory="chroma_store")
        self.db = db
        return db

    def specific_embeddings (self , files): 
        retriever = self.db.as_retriever(search_kwargs={
        "filter": {"source": {"$in": files}}
        })
        self.retriever = retriever
        return retriever

    def RetrievalQA (self , query ) : 
        os.environ["TOGETHER_API_KEY"] = "018548f37134ff50a4244bec41ae87fa4b7ede1695be79f422aa7fb13f77e414"
        model = ChatTogether(
            model=self.model_name
        )
        if self.retriever == "" : 
            retriever = self.db.as_retriever()
            qa_chain = RetrievalQA.from_chain_type(llm=model, retriever=retriever)
        else : 
            qa_chain = RetrievalQA.from_chain_type(llm=model, retriever=self.retriever)
        self.chain = qa_chain
        self.template = PromptTemplate.from_template(template=query)
    def answer (self , query ) : 
        prompt_formatted_str: str = self.template.format(
            question=query)
        response = self.chain.invoke(prompt_formatted_str)
        return response.get("result", response)


