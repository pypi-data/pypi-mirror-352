"""Prompt for sentiment score of customer product reviews."""

PROMPT = """
    System Message:\n
    Provide a floating-point representation of the sentiment of the following customer product review that is rounded to five decimal places.\n
    The scale ranges from -1.0 (negative) to 1.0 (positive), where 0.0 represents neutral sentiment.\n
    Only return the sentiment score value and nothing else.\n
    You may only return a single numeric value.\n\n
    User Message:\n
    Conversation:\n{transcribed_and_diarized}
"""
