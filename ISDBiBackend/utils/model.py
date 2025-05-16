
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_together import ChatTogether
import os
from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain.schema import Document
import requests
from langchain.embeddings.base import Embeddings

class ollama_embeddings(Embeddings):
    def __init__(self, model, url):
        self.model = model
        self.url = url

    def embed_documents(self, texts):
        return [self._embed(text) for text in texts]
    
    def embed_query(self, text):
        return self._embed(text)

    def _embed(self, text):
        response = requests.post(
            f"{self.url}/api/embeddings",
            json={"model": self.model, "prompt": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]


def load_all_documents (pdf_path , chunk_size = 500 , chunk_overlap = 100 ) :
    chunks = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    for path in pdf_path : 
        loader = PyPDFLoader(path)
        document = loader.load()
        # Add file name as metadata
        for doc in document:
            doc.metadata["source"] = os.path.basename(path)
            print (doc.metadata["source"])
        chunks += splitter.split_documents(document)
    embeddings = ollama_embeddings(model="mxbai-embed-large", url="http://localhost:11434")
    db = Chroma.from_documents(chunks, embedding=embeddings, persist_directory="../chroma_store")
    return db


class RAGModel : 
    def __init__ (self , db ,model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free" , 
                  chunk_size = 500 , 
                  chunk_overlap = 100  ) :
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.pdf_path = []
        self.documents = []
        self.chain = ""
        self.db = db
        self.template = "" 
        self.retriever = ""
    
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
    def invoke (self , query ) : 
        prompt_formatted_str: str = self.template.format(
            question=query)
        response = self.chain.invoke(prompt_formatted_str)
        return response.get("result", response)



    
    
        

if __name__ == '__main__' : 
    
    db = load_all_documents(["./books/blue_sisters.pdf" , "./books/normal_people.pdf"])
    model = RAGModel(db)
    template = "you are a book chatbot. Answer the question based on the books you have read. {question}"
    model.RetrievalQA(template)
    query = "is Connell a good friend?"
    print ("correct embedding , general one ")
    response = model.invoke(query)
    print (response )
    model.specific_embeddings(["blue_sisters.pdf"])
    model.RetrievalQA(template)
    query = "is Connel a good friend ? "
    print ("specific embeddings , wrong ones ")
    response = model.invoke(query)
    print(response)

