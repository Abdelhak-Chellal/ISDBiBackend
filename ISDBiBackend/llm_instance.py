
# ISDBiBackend/llm_instance.py

import os
from utils.model import load_all_documents, RAGModel

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
