from model import RAGModel
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI 
from model import load_all_documents

class multiAgents : 
    def __init__ (self , db , reviewer_query , proposer_query ,validator_query  , number_validators=3  , number_proposers = 3 , number_reviews=3   ): 
        self.number_validators = number_validators
        self.number_proposers = number_proposers
        self.number_reviews = number_reviews
        self.db = db
        self.reviewer = [RAGModel(db) for _ in range(number_reviews)]
        self.proposer = [RAGModel(db) for _ in range(number_proposers)]
        self.validator = [RAGModel(db) for _ in range(number_validators)]
        for _ in range(number_reviews):
            self.reviewer[_].RetrievalQA(reviewer_query)
        for _ in range(number_proposers):
            self.proposer[_].RetrievalQA(proposer_query)
        for _ in range(number_validators):  
            self.validator[_].RetrievalQA(validator_query)
    def invoke (self , query  ) :
        review = ""
        proposal = ""
        validator = ""
        for _ in range (self.number_reviews) : 
            review += self.reviewer[_].invoke(query )
        for _ in range (self.number_proposers) : 
            proposal  += self.proposer[_].invoke(review )
        for _ in range (self.number_validators) : 
            validator  += self.validator[_].invoke(proposal )
        return review , proposal , validator
    
if __name__ ==  "__main__" : 
     db = load_all_documents([
        "Data/FI5F55_1_Musharaka Financing(4).PDF",
    "Data/FI28ED_1_Salam and Parallel Salam (07).PDF",
    "Data/FI922A_1_Murabaha and Other Deferred Payment Sales (28).PDF",
    "Data/FINANC_1_Istisnaa and Parallel Istisnaa (10).PDF",
    "Data/Ijarah (32).pdf",
    "Data/SS - shariah-standards-2015-321-390 (1) 1.pdf",
    "Data/SS8 - Murabahah - revised standard.pdf",
    "Data/SS9 - Ijarah and Ijarah Muntahia Bittamleek - revised standard.pdf",
    "Data/SS10 - Salam and Parallel Salam - revised standard.pdf"
    ])
     
     print("Loading shared embedding database...")
     query = ""
     review = ""
     proposal = ""
     reviewer = f"""
        You are a ReviewerAgent. Extract key Islamic finance compliance points from this text based on the FAS standards:
        Text:
        {query}

        Output:
        - List the most relevant compliance-relevant features or concerns.
    """
     proposer = f"""
        You are a ProposalAgent. Based on the extracted compliance points, propose a solution or recommendation:
        Text:
        {review}

        Output:
        - List the proposed solutions or recommendations.
    """
     validator = f"""
        You are a ValidationAgent. Validate the proposed solutions and provide a consensus score:
        Text:   
        {proposal}
        Output:
        - Provide a verdict (Approved/Rejected) based on the consensus score. give reasons for the verdict.
        - List the consensus score.
    """


     pipeline = multiAgents(db, reviewer , proposer , validator  , number_validators=1 , number_proposers=1 , number_reviews=1)
     query = """
Bitcoin is a decentralized digital asset. It is not backed by tangible commodities. It is highly volatile, often traded for speculative purposes, and can be used anonymously.
"""
     review , proposal , validator = pipeline.invoke(query)
     print("Review:", review)
     print("Proposal:", proposal)    
     print("Validator:", validator)