"""Prompt for summarizing customer support conversations (sk)."""

PROMPT = """
    System Message:
    You are a helpful assistant for analyzing and summarizing customer support conversations.
    User Message:
    Conversation: {transcribed_and_diarized}

    Your task is to analyze and summarize the O2 sales conversation. The output must include:
        - One call category from these: Fakturácia, Zabezpečenie služby, Technická podpora, Podpora zariadení, Roaming, Retencia, Podvod, Sťažnosť, Predaj. \n
        - The reason for the customer's contact with support. Provide it as a concise noun phrase (not a full sentence), clearly summarizing the core issue. \n
        - A brief description of the resolution process and the outcome. Brief and concise, max 2 sentences.\n
        - The company's products from these: O2 Spolu, Mobilné služby, Internet, TV, Telefóny a zariadenia. \n
        - Customer's satisfaction is either -1 (negative), 1 (positive) or 0 (neutral) where 0 represents neutral sentiment. \n

        - If follow-up call necessary, then True, else False. \n
        - Tone of voice on the scale from 1 to 5 for these pairs, assigning 1 more close to the first pair and 5 to the second:
            1. formal -> casual
            2. serious -> funny
            3. respectfully -> irreverent
            4. matter of fact -> enthusiastic \n
        - A comma-separated list of **maximum five tags** that capture key phrases or attributes from the conversation relevant to sales outcomes. \n
        - From those tags, infer whether the aspects present in the conversation align with positive sales behaviours (e.g., friendly tone, proactive assistance) or negative ones (e.g., rude tone, unhelpful responses). \n
        - Evaluate how well the support agent adheres to **positive aspects** and avoids **negative aspects**, based on observed language and approach. \n
    The summary should not include:
        - Personal information of the customer and operator (e.g., names, addresses).
        - Greetings exchanged between the customer and operator. \n
    Return result as simple JSON:
        {{
            "category": "string",
            "reason": "string",
            "description": "string",
            "products": ["string1", "string2", ...],
            "satisfaction": int,
            "fup": bool,
            "tone_of_voice": {{
                "formal_casual": int,
                "serious_funny": int,
                "respect_irreverent": int,
                "mof_enthusiastic": int,
                }},
            "tags": ["string1", "string2", ...],
            "aspects_evaluation": {{
            "positive_aspects_present": ["string1", "string2", ...],
            "negative_aspects_present": ["string1", "string2", ...],
            "agent_performance": "string"
        }} \n
        The output MUST be in slovak! NO english should be present outside of the JSON keys. \n

        Return a valid JSON object that can ALWAYS be parsed without errors.
"""
