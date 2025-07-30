"""Prompts for tagging conversations."""

PROMPT = """
    System Message:\n
    You are a helpful analysis of transactional sales data.\n\n
    User Message:\n
    Return a comma-separated list of maximum five tags for the following conversation.\n\n
    Conversation:\n{transcribed_and_diarized}
"""
