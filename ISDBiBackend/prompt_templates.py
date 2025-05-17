# Prompt templates
template = "hello hello"
USE_CASE_TEMPLATE = f"""
    "Given the following Islamic finance transaction: {{template}}. "
    "Identify the applicable AAOIFI Financial Accounting Standard(s). "
    "Calculate the bank's profit using the appropriate method. "
    "Provide detailed accounting entries at each phase of the transaction (e.g., each quarter), "
    "applying the percentage-of-completion method where appropriate. "
    "Finally, summarize the ledger over the contract duration using a visual table format showing each quarter’s percentage of completion, "
    "revenue recognized, cost incurred, and profit recognized."
"""



REVERSE_TX_TEMPLATE = f"""
The following financial event occurred: {{template}}. 
Identify the applicable AAOIFI FAS standard(s). If more than one standard may apply, assign a weighted likelihood 
(e.g., in percentage or score) to each, based on relevance. Justify your reasoning for each choice. Then, provide the correct 
accounting treatment in the form of journal entries.
"""



REVERSE_TX_TEMPLATE_2 = f"""
Example:
Context: GreenTech exits in Year 3, and Al Baraka Bank buys out its stake.
Adjustments:
- Buyout Price: $1,750,000
- Bank Ownership: 100%
- Accounting Treatment:
  - Derecognition of GreenTech’s equity
  - Recognition of acquisition expense
- Journal Entry for Buyout:
  Dr. Investment in GreenTech       1,750,000
      Cr. Cash                      1,750,000
(To record acquisition of GreenTech’s equity)

Applicable Standards:
1. FAS 4 – 70% – Applies because the transaction affects presentation of equity in financial statements.
2. FAS 20 – 30% – May apply if the investment was accounted for using the equity method.
3. FAS 32 – 0% – Not relevant; applies only to Ijarah (leasing) transactions.

Explanation:
- FAS 4 is the most relevant due to its coverage of equity transactions and financial statement presentation.
- FAS 20 may be considered based on the nature of GreenTech's relationship to the bank (e.g., associate).
- FAS 32 is commonly confused but not applicable here as this is not a lease.

---

Now, perform the same analysis for the following:

The following financial event occurred: {{template}}
Based on AAOIFI Financial Accounting Standards (FAS), identify all potentially applicable standards from FAS 4, FAS 32, FAS 7, FAS 10, and FAS 28.

For each applicable standard, provide a relevance score or percentage (based on how directly it applies).

Rank the standards from most to least relevant.

Justify your selection for each standard in 1–2 sentences.

Then, provide the correct accounting treatment by showing the journal entries, with clear account names and explanations.

If any standards are commonly confused or misapplied (e.g., FAS 32 used instead of FAS 4), explain why they are not relevant.
"""


AUDIT_TEMPLATE = f"""
You are an Islamic finance audit analysis agent.

Your task is to audit the following financial record or decision using only AAOIFI Governance Standards (GS).

---

🔸 Instructions:
- Use **only** the relevant AAOIFI standards.
- Identify any **non-compliance**, **missing audit steps**, or **violations of internal control or Shari’ah governance**.
- Be concise, yet specific.
- If the input is incomplete, clearly list **what additional audit information is required**.
- Do **not reference any non-AAOIFI frameworks**.

---

🔸 Output Format:
- **Compliance Status**: Compliant / Non-Compliant / Inconclusive
- **Findings**: Bullet list of audit observations
- **Applicable AAOIFI Standard(s)**: GS or FAS with clause number(s)
- **Suggestions**: (Optional, if improvement is possible)

Example:

Compliance Status: Non-Compliant

Findings:
- No record of independent internal Shari’ah audit (GS 10, Clause 4.1)
- Board approval did not include documented review by Shari’ah Supervisory Board (GS 11, Clause 6.2)

Applicable AAOIFI Standards:
- GS 10: Internal Shari’ah Audit (Clause 4.1, 4.3)
- GS 11: Shari’ah Compliance Function (Clause 6.2)

Suggestions:
- Conduct retrospective internal audit
- Document all board-level Shari’ah approvals formally
"""


FRAUD_DETECTION_TEMPLATE = f"""
You are a fraud detection agent for Islamic financial institutions.
Your task is to analyze the following based only on the provided AAOIFI standards 
to determine if it complies with Shari’ah principles. If it does not comply, flag it as potential fraud 
and provide a clear explanation.

Input:
 Details:
{{template}}

Instructions:
- Use only the provided AAOIFI standards (FAS, GS, SS) for your analysis.
- Do not reference any external or non-AAOIFI frameworks.
- Clearly flag any violation such as:
  - Conflict of interest
  - Undisclosed riba
  - Deviation from contract structure or purpose
  - Fake, missing, or incomplete audit trail
- Be specific, objective, and concise.
- If the input is unclear or incomplete, state what additional details are needed.

Output Format:

Compliance: Yes / No / Unclear

Explanation:
- [If No] Describe why is not Shari’ah-compliant
- Mention any suspicious activity or deviation
- Use relevant clauses if possible (e.g., GS 11 Clause 6.2)

Applicable AAOIFI Standards:
- List the standards (e.g., FAS 8, GS 11 Clause 7.1)

Recommendations (Optional):
- Suggest corrective steps if applicable
"""


# -------------------- files

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


external_files = [    "../Data/AAOIFI-GS-10-Shariah-Compliance-and-Fiduciary-Ratings-for-IFIs-Final-for-Issuance-CS-Clean-1.pdf",
    "../Data/AAOIFI-GS-11-Internal-Shariah-Audit-Final-for-Issuance-CS.pdf",
    "../Data/Auditing-standard-No.-1-Objective-and-Principles-of-Auditing.pdf",
    "../Data/Auditing-standard-No.-2-Auditors-Report.pdf",
    "../Data/Auditing-standard-No.-3-Terms-of-Audit-Engagement.pdf",
    "../Data/Auditing-standard-No.-4-Testing-for-Compliance-with-Sharia-Rules-and-Principles-by-an-External-Auditor-2.pdf",
    "../Data/Auditing-standard-No.-5-Auditors-Responsibility-to-Consider-Fraud-and-Error-in-an-Audit-of-Financial-Statements-2.pdf"
    ]