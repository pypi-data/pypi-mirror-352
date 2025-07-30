"""Prompt for summarizing customer support conversations."""

PROMPT = """
    System Message:
    You are a helpful assistant for analyzing and summarizing customer support conversations.

    User Message:
    Conversation:{transcribed_and_diarized}
    Your task is to analyze and summarize the O2 sales conversation. The output must include:
        - One call category from these: Billing, Service Provisioning, Technical Support, Device Support, Roaming, Retention, Fraud, Complaints, Sales.
        - The reason for the customer's contact with support.
        - A brief description of the resolution process and the outcome.
        - The company's products from these: O2 Spolu, Mobilné služby, Internet, TV, Telefóny a zariadenia.
        - Customer's satisfaction is either -1 (negative), 1 (positive) or 0 (neutral) where 0 represents neutral sentiment.

        - If follow-up call necessary, then True, else False.
        - Tone of voice on the scale from 1 to 5 for these pairs, assigning 1 more close to the first pair and 5 to the second:
            1. formal -> casual
            2. serious -> funny
            3. respectfully -> irreverent
            4. matter of fact -> enthusiastic
        - A comma-separated list of **maximum five tags** that capture key phrases or attributes from the conversation relevant to sales outcomes.
        - From those tags, infer whether the aspects present in the conversation align with positive sales behaviors (e.g., friendly tone, proactive assistance) or negative ones (e.g., rude tone, unhelpful responses).
        - Evaluate how well the support agent adheres to **positive aspects** and avoids **negative aspects**, based on observed language and approach.

    The summary should not include:
        - Personal information of the customer and operator (e.g., names, addresses).
        - Greetings exchanged between the customer and operator.

    Return result as simple JSON:
        {{
            "category": "",
            "reason": "",
            "description": "",
            "products": [""],
            "satisfaction": "",
            "fup": "",
            "tone_of_voice": {{
                "formal_casual": "",
                "serious_funny": "",
                "respect_irreverent": "",
                "mof_enthusiastic": "",
                }},
            "tags": [""],
            "aspects_evaluation": {{
            "positive_aspects_present": [""],
            "negative_aspects_present": [""],
            "agent_performance": ""
        }}
"""
