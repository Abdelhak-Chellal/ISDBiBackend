
# ISDBiBackend/llm_instance.py

import os
from utils.model import load_all_documents, RAGModel
import asyncio
from langchain_together import ChatTogether
import re 

from prompt_templates import USE_CASE_TEMPLATE, REVERSE_TX_TEMPLATE, REVERSE_TX_TEMPLATE_2
from prompt_templates import AUDIT_TEMPLATE, FRAUD_DETECTION_TEMPLATE
from prompt_templates import files, fas_files, external_files



print("🔄 Loading shared embedding database...")

# Load shared Chroma DB from disk
db = load_all_documents(external_files) 

print("-------------------------------------")

print("done Loading shared embedding database")


# Ensure the Chroma DB was previously created and persisted in "chroma_store"
if not os.path.exists("../chroma_store"):
    raise RuntimeError("❌ Chroma DB not found! Run the embedding step first.")



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


def fraud_detect_llm():
    llm = RAGModel(db)
    llm.specific_embeddings(external_files)
    llm.RetrievalQA(FRAUD_DETECTION_TEMPLATE)
    return llm 


def auditing_llm():
    llm = RAGModel(db)
    llm.specific_embeddings(external_files)
    llm.RetrievalQA(AUDIT_TEMPLATE)
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
    os.environ["TOGETHER_API_KEY"] = "dfcd8c728ca6b1f456ee4ffc06ea3cec55434b09d6b0fbfbccc51caec5d6c1fb"
    model = ChatTogether(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo"
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

    
            
    def invoke(self, query):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Step 1: Reviewers
        review_results = loop.run_until_complete(self._parallel_invoke(self.reviewer, query))
        combined_review = "\n---\n".join(review_results)
        try:
            summarized_review = summarizer(combined_review)
        except Exception as e:
            summarized_review = f"Summarization failed at review stage: {str(e)}"

        # Step 2: Proposers (input is the summarized review)
        proposal_results = loop.run_until_complete(self._parallel_invoke(self.proposer, summarized_review))
        combined_proposal = "\n---\n".join(proposal_results)
        try:
            summarized_proposal = summarizer(combined_proposal)
        except Exception as e:
            summarized_proposal = f"Summarization failed at proposal stage: {str(e)}"

        # Step 3: Validators (input is the summarized proposal)
        validator_results = loop.run_until_complete(self._parallel_invoke(self.validator, summarized_proposal))
        combined_validator = "\n---\n".join(validator_results)
        try:
            summarized_validator = summarizer(combined_validator)
        except Exception as e:
            summarized_validator = f"Summarization failed at validator stage: {str(e)}"
        
        loop.close()

        return {
            "raw": {
                "review": combined_review,
                "proposal": combined_proposal,
                "validator": combined_validator,
            },
            "summaries": {
                "review": summarized_review,
                "proposal": summarized_proposal,
                "validator": summarized_validator,
            },
        }


def standard_enhancement_llm(template):
    review = ""
    proposal = ""
    reviewer = f"""
    You are a Review Agent in an Islamic finance and AAOIFI FAS (Financial Accounting Standards) multi-agent system.
    you will read batch of news reports and identify elements that relate directly to Shariah compliance or that may require updates or clarifications in the standards


    <text>
    {{template}}
    </text>
    Instructions:
        Extract clear, individual points that could trigger concern or updates in the standard.,
        Relate your findings to specific FAS principles (e.g., riba, gharar, transparency).,
        Use the tag format for structured output.

   
    - Presence of interest-based terms violates FAS X, which prohibits riba.
    
    - Lack of clear ownership structure may conflict with FAS Y related to asset-backed securities.
    
    """

    proposer = f"""
    You are a Proposal Agent with expertise in Shariah-compliant finance and Islamic standard developement. Given the reviewer observations and the current AAOIFI standard clause, propose enhancements or clarifications to the standard mentioned as follows : 

    <text>
    {{template}}
    </text>
    Instructions:

        Propose modifications that clarify, update, or extend the standard.,
        Ensure proposals are justified by the reviewer points and maintain Shariah integrity.
   ]
    - Replace interest-based financing with a mudarabah contract structure.
    
    - Introduce detailed asset disclosure to meet FAS Z transparency requirements.
    
    """


    validator = f"""
You are a Validation Agent in an Islamic finance multi-agent system. Assess the proposed recommendations for Shariah compliance using AAOIFI FAS mentioned in the following proposal:

<text>
{{template}}
</text>

Instructions:

For each proposal, provide:

- **Verdict** (Approved/Rejected),
- **Justification** referencing Shariah concepts or FAS clauses,
- A **Consensus Score** between 0 (non-compliant) and 1 (fully compliant)

Output Format (Use [VALIDATION]...[/VALIDATION] tags):

[VALIDATION]
**🟢 Verdict:** Approved  
**Reason:** Mudarabah contracts are compliant under FAS X and avoid riba.  
**Consensus Score:** 0.92
[/VALIDATION]

[VALIDATION]
**🔴 Verdict:** Rejected  
**Reason:** Disclosure plan lacks asset classification detail required by FAS Y.  
**Consensus Score:** 0.45
[/VALIDATION]
"""



    os.environ["TOGETHER_API_KEY"] = "dfcd8c728ca6b1f456ee4ffc06ea3cec55434b09d6b0fbfbccc51caec5d6c1fb"

    pipeline = multiAgents(db, reviewer, proposer, validator,
                        number_validators=3, number_proposers=3, number_reviews=1)

    result = pipeline.invoke(template)
    return result


def summarizer(list_responses):
    if isinstance(list_responses, list):
        list_responses = "\n---\n".join(list_responses)

    os.environ["TOGETHER_API_KEY"] = "dfcd8c728ca6b1f456ee4ffc06ea3cec55434b09d6b0fbfbccc51caec5d6c1fb"
    model = ChatTogether(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo"
    )

    prompt = f"""
    You are an intelligent summarization agent.

    Your task is to read multiple responses and produce a *coherent, concise, and informative summary*. Your summary should:
    - Highlight the key points from all responses
    - Avoid repetition
    - Use clear and professional language
    - Group related ideas together when possible

    Below are the responses:

    --- RESPONSES ---
    {list_responses}

    --- SUMMARY ---
    """

    response = model.invoke(prompt)
    return response.content