
# ISDBiBackend/llm_instance.py

import os
from utils.model import load_all_documents, RAGModel
import asyncio
from langchain_together import ChatTogether


fas_files = [
    "FI5F55_1_Musharaka Financing(4).PDF",
    "FI28ED_1_Salam and Parallel Salam (07).PDF",
    "FI922A_1_Murabaha and Other Deferred Payment Sales (28).PDF",
    "FINANC_1_Istisnaa and Parallel Istisnaa (10).PDF",
    "Ijarah (32).pdf"
]

files = [
    "../Data/FI5F55_1_Musharaka Financing(4).PDF",
    "../Data/FI28ED_1_Salam and Parallel Salam (07).PDF",
    "../Data/FI922A_1_Murabaha and Other Deferred Payment Sales (28).PDF",
    "../Data/FINANC_1_Istisnaa and Parallel Istisnaa (10).PDF",
    "../Data/Ijarah (32).pdf",
]
files_ss = [    "../Data/SS - shariah-standards-2015-321-390 (1) 1.pdf",
    "../Data/SS8 - Murabahah - revised standard.pdf",
    "../Data/SS9 - Ijarah and Ijarah Muntahia Bittamleek - revised standard.pdf",
    "../Data/SS10 - Salam and Parallel Salam - revised standard.pdf"]

print("🔄 Loading shared embedding database...")

# Load shared Chroma DB from disk
db = load_all_documents(files) 

print("-------------------------------------")

print("done Loading shared embedding database")


# Ensure the Chroma DB was previously created and persisted in "chroma_store"
if not os.path.exists("../chroma_store"):
    raise RuntimeError("❌ Chroma DB not found! Run the embedding step first.")





# Prompt templates
USE_CASE_TEMPLATE = (
    "Given the following Islamic finance transaction: {question}. "
    "Identify the applicable AAOIFI Financial Accounting Standard(s). "
    "Calculate the bank's profit using the appropriate method. "
    "Provide detailed accounting entries at each phase of the transaction (e.g., each quarter), "
    "applying the percentage-of-completion method where appropriate. "
    "Finally, summarize the ledger over the contract duration using a visual table format showing each quarter’s percentage of completion, "
    "revenue recognized, cost incurred, and profit recognized."
)


REVERSE_TX_TEMPLATE = (
    "The following financial event occurred: {question}. "
    "Identify the applicable AAOIFI FAS standard(s). If more than one standard may apply, assign a weighted likelihood "
    "(e.g., in percentage or score) to each, based on relevance. Justify your reasoning for each choice. Then, provide the correct "
    "accounting treatment in the form of journal entries."
)

REVERSE_TX_TEMPLATE_2 = (
    "Example:\n"
    "Context: GreenTech exits in Year 3, and Al Baraka Bank buys out its stake.\n"
    "Adjustments:\n"
    "- Buyout Price: $1,750,000\n"
    "- Bank Ownership: 100%\n"
    "- Accounting Treatment:\n"
    "  - Derecognition of GreenTech’s equity\n"
    "  - Recognition of acquisition expense\n"
    "- Journal Entry for Buyout:\n"
    "  Dr. Investment in GreenTech       1,750,000\n"
    "      Cr. Cash                      1,750,000\n"
    "(To record acquisition of GreenTech’s equity)\n"
    "\n"
    "Applicable Standards:\n"
    "1. FAS 4 – 70% – Applies because the transaction affects presentation of equity in financial statements.\n"
    "2. FAS 20 – 30% – May apply if the investment was accounted for using the equity method.\n"
    "3. FAS 32 – 0% – Not relevant; applies only to Ijarah (leasing) transactions.\n"
    "\n"
    "Explanation:\n"
    "- FAS 4 is the most relevant due to its coverage of equity transactions and financial statement presentation.\n"
    "- FAS 20 may be considered based on the nature of GreenTech's relationship to the bank (e.g., associate).\n"
    "- FAS 32 is commonly confused but not applicable here as this is not a lease.\n"
    "\n"
    "---\n"
    "\n"
    "Now, perform the same analysis for the following:\n"
    "\n"
    "The following financial event occurred: {question}\n"
    "Based on AAOIFI Financial Accounting Standards (FAS), identify all potentially applicable standards from FAS 4, FAS 32, FAS 7, FAS 10, and FAS 28.\n\n"
    "For each applicable standard, provide a relevance score or percentage (based on how directly it applies).\n\n"
    "Rank the standards from most to least relevant.\n\n"
    "Justify your selection for each standard in 1–2 sentences.\n\n"
    "Then, provide the correct accounting treatment by showing the journal entries, with clear account names and explanations.\n\n"
    "If any standards are commonly confused or misapplied (e.g., FAS 32 used instead of FAS 4), explain why they are not relevant."
)


# Answering functions
def use_case_llm():
    llm = RAGModel(db)
    llm.specific_embeddings(fas_files)
    llm.RetrievalQA(USE_CASE_TEMPLATE)
    return llm 

def reverse_tx_llm():
    llm = RAGModel(db)
    llm.specific_embeddings(fas_files)
    llm.RetrievalQA(REVERSE_TX_TEMPLATE_2)
    return llm 



# Async wrapper for LLM calls
async def async_llm_invoke(llm, question):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, llm.invoke, question)


def product_design_llm(question):
    # Step 1: Run both use_case and reverse_tx in parallel
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    use_case_llm_instance = use_case_llm()
    reverse_tx_llm_instance = reverse_tx_llm()
    results = loop.run_until_complete(asyncio.gather(
        async_llm_invoke(use_case_llm_instance, question),
        async_llm_invoke(reverse_tx_llm_instance, question),
    ))
    loop.close()

    use_case_answer, reverse_tx_answer = results

    # Step 2: Combine the responses into a single prompt
    prompt = f"""
    You are a Financial Product Report Generator. Given the outputs of two agents — one analyzing the transaction structure and accounting flow (UseCaseAgent), one assessing edge cases (ReverseAgent) produce a unified, clear, and concise report. The report should include:

    1. Recommended product structure and contract type  
    2. Applicable AAOIFI FAS and SS standards  
    3. Profit calculation and recognition method  
    4. Quarter-by-quarter journal entries  
    5. Summary ledger in tabular format  
    6. Risk scenario analysis (e.g., default, impairment) with journal entries and weighted FAS application  
    8. Justifications for each decision and enhancement

    --- UseCaseAgent Output ---
    {use_case_answer}

    --- ReverseAgent Output ---
    {reverse_tx_answer}

    (Assume the EnhancementAgent expands the relevant AAOIFI standards with improvements where needed.)
    """

    # Step 3: Call LLaMA 3.3-70B for synthesis
    os.environ["TOGETHER_API_KEY"] = "018548f37134ff50a4244bec41ae87fa4b7ede1695be79f422aa7fb13f77e414"
    model = ChatTogether(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    )
    response = model.invoke(prompt)
    print(response)
    return response.content


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
    
def standard_enhancement_llm(question):
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
     os.environ["TOGETHER_API_KEY"] = "018548f37134ff50a4244bec41ae87fa4b7ede1695be79f422aa7fb13f77e414"
    
     pipeline = multiAgents(db, reviewer , proposer , validator  , number_validators=1 , number_proposers=1 , number_reviews=1)
     
     review , proposal , validator = pipeline.invoke(query)
     print("Review:", review)
     print("Proposal:", proposal)    
     print("Validator:", validator)
     return review , proposal , validator

    