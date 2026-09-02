BUSINESS_REPORT_SYSTEM_PROMPT = """
You are the business analysis assistant for Business Pulse,
an application designed for small and medium-sized businesses.

Your job is to analyze business performance data and provide
clear, practical insights for the business owner.

Rules:
- Use only the information provided.
- Do not invent numbers or facts.
- Focus on important business trends and problems.
- Explain insights in simple language.
- Avoid unnecessary technical or financial jargon.
- Give practical recommendations when appropriate.
- Keep the response concise.
- Do not repeat the entire dataset.
"""

BUSINESS_CHAT_SYSTEM_PROMPT = """
You are Business Pulse, a business analysis assistant
for small and medium-sized businesses.

Your job is to answer questions about the business data
provided to you.

Rules:
- Use only the information provided.
- Do not invent numbers or facts.
- If the information needed to answer a question is not
  available, say so clearly.
- Use simple language.
- Give direct answers.
- Keep responses concise.
"""

def build_business_report_prompt(summary: dict) -> str:
    """
    Build a prompt for analyzing a Business Pulse report.
    """

    return f"""
Analyze the following business report:

Sales:
- Number of sales: {summary["number_of_sales"]}
- Total sales: ₦{summary["total_sales"]:,.2f}
- Total paid: ₦{summary["total_paid"]:,.2f}
- Credit outstanding: ₦{summary["total_credit"]:,.2f}
- Collection rate: {summary["collection_rate"]:.2f}%
- Credit rate:{summary["credit_rate"]:.2f}%

Purchases:
- Number of purchases: {summary["number_of_purchases"]}
- Total purchases: ₦{summary["total_purchases"]:,.2f}

Provide:

1. Key business insights
2. Potential concerns
3. Practical recommendations

Keep the response concise and easy for a small business owner to understand.
"""

def build_business_chat_prompt(
    summary: dict,
    user_question: str,
) -> str:
    """
    Build a prompt for answering a question about a
    Business Pulse report.
    """

    return f"""
Business report:

Sales:
- Number of sales: {summary["number_of_sales"]}
- Total sales: ₦{summary["total_sales"]:,.2f}
- Total paid: ₦{summary["total_paid"]:,.2f}
- Credit outstanding: ₦{summary["total_credit"]:,.2f}
- Average sale: ₦{summary["average_sale"]:,.2f}
- Collection rate: {summary["collection_rate"]:.2f}%
- Credit rate: {summary["credit_rate"]:.2f}%

Purchases:
- Number of purchases: {summary["number_of_purchases"]}
- Total purchases: ₦{summary["total_purchases"]:,.2f}

Gross difference:
₦{summary["total_sales"] - summary["total_purchases"]:,.2f}

User question:
{user_question}

Answer the user's question using the business report above.
"""