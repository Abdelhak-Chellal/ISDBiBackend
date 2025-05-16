
# ISDBiBackend/llm_instance.py

import os
from utils.model import load_all_documents, RAGModel
import asyncio
from langchain_together import ChatTogether
import re 


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
        model="deepseek-ai/deepseek-llm-67b-base"
    )
    response = model.invoke(prompt)
    print(response)
    return response.content


class multiAgents:
    def __init__(self, db, reviewer_query, proposer_query, validator_query,
                 number_validators=3, number_proposers=3, number_reviews=3):
        self.number_validators = number_validators
        self.number_proposers = number_proposers
        self.number_reviews = number_reviews
        self.db = db
        self.reviewer = [RAGModel(db) for _ in range(number_reviews)]
        self.proposer = [RAGModel(db) for _ in range(number_proposers)]
        self.validator = [RAGModel(db) for _ in range(number_validators)]

        for i in range(number_reviews):
            self.reviewer[i].RetrievalQA(reviewer_query)
        for i in range(number_proposers):
            self.proposer[i].RetrievalQA(proposer_query)
        for i in range(number_validators):
            self.validator[i].RetrievalQA(validator_query)

    async def _parallel_invoke(self, agents, query):
        loop = asyncio.get_event_loop()
        return await asyncio.gather(*[
            loop.run_in_executor(None, agent.invoke, query) for agent in agents
        ])
    def extract_scores(outputs):
        scores = []
        for text in outputs:
            # Extract consensus score using regex
            match = re.search(r"Consensus Score\s*[:\-]?\s*([0-9]*\.?[0-9]+)", text)
            if match:
                score = float(match.group(1))
                scores.append(score)
        return scores

    def decide_final_verdict(avg_score, threshold=0.75):
        if avg_score >= threshold:
            return "Approved"
        else:
            return "Rejected"
        
    def invoke(self, query):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Step 1: Reviewers
        review_results = loop.run_until_complete(self._parallel_invoke(self.reviewer, query))
        combined_review = "\n---\n".join(review_results)

        # Step 2: Proposers (input is the combined review)
        proposal_results = loop.run_until_complete(self._parallel_invoke(self.proposer, combined_review))
        combined_proposal = "\n---\n".join(proposal_results)

        # Step 3: Validators (input is the combined proposal)
        validator_results = loop.run_until_complete(self._parallel_invoke(self.validator, combined_proposal))
        combined_validator = "\n---\n".join(validator_results)

        # Score extraction & verdict aggregation
        scores = self.extract_scores(validator_results)
        avg_score = sum(scores) / len(scores) if scores else 0
        final_verdict = self.decide_final_verdict(avg_score)

        loop.close()

        return {
        "review": combined_review,
        "proposal": combined_proposal,
        "validator_raw": combined_validator,
        "validator_scores": scores,
        "validator_average": round(avg_score, 3),
        "final_verdict": final_verdict
    }
    

def standard_enhancement_llm(template):
    review = ""
    proposal = ""
    reviewer = f"""
You are an Islamic Finance Reviewer Agent specializing in AAOIFI Financial Accounting Standards (FAS).
Analyze the following text and extract key Shariah compliance issues or relevant features based on FAS standards.

<text>
{template}
</text>

Output Format (Use [REVIEW]...[/REVIEW] tags for each point):
[REVIEW]
- Presence of interest-based terms violates FAS X, which prohibits riba.
[/REVIEW]
[REVIEW]
- Lack of clear ownership structure may conflict with FAS Y related to asset-backed securities.
[/REVIEW]
"""

    proposer = f"""
You are a Proposal Agent with expertise in Islamic finance. Based on the extracted [REVIEW] points, propose clear Shariah-compliant solutions or recommendations in line with AAOIFI FAS.

<text>
{template}
</text>

Output Format (Use [PROPOSAL]...[/PROPOSAL] tags for each proposal):
[PROPOSAL]
- Replace interest-based financing with a mudarabah contract structure.
[/PROPOSAL]
[PROPOSAL]
- Introduce detailed asset disclosure to meet FAS Z transparency requirements.
[/PROPOSAL]
"""


    validator = f"""
You are a Validation Agent in an Islamic finance multi-agent system. Assess the proposed [PROPOSAL] recommendations for Shariah compliance using AAOIFI FAS.

<text>
{template}
</text>

Instructions:
- For each [PROPOSAL], give a verdict (Approved/Rejected) and specific reasoning tied to FAS guidelines.
- Assign a consensus score between 0 and 1 (e.g., 0.75 = moderately compliant).

Output Format (Use [VALIDATION]...[/VALIDATION]):
[VALIDATION]
Verdict: Approved  
Reason: Mudarabah contracts are compliant under FAS X and avoid riba.  
Consensus Score: 0.92
[/VALIDATION]
[VALIDATION]
Verdict: Rejected  
Reason: Disclosure plan lacks asset classification detail required by FAS Y.  
Consensus Score: 0.45
[/VALIDATION]
"""


    os.environ["TOGETHER_API_KEY"] = "018548f37134ff50a4244bec41ae87fa4b7ede1695be79f422aa7fb13f77e414"

    pipeline = multiAgents(db, reviewer, proposer, validator,
                           number_validators=3, number_proposers=3, number_reviews=3)

    result = pipeline.invoke(template)
    print("🔍 Review:\n", result["review"])
    print("\n💡 Proposal:\n", result["proposal"])
    print("\n🛡️ Validator Raw Output:\n", result["validator_raw"])
    print("\n📊 Validator Scores:", result["validator_scores"])
    print("📈 Average Score:", result["validator_average"])
    print("✅ Final Verdict:", result["final_verdict"])
    return result

    