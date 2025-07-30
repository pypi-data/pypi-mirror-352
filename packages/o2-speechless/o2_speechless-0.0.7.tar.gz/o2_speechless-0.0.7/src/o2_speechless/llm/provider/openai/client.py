"""OpenAI API client for the Scout app."""

import requests
import json
from functools import lru_cache
import importlib
from typing import Any

TIMEOUT_SECONDS = 30

_PACKAGE = "o2_speechless.llm.provider.openai.constants.prompts"


@lru_cache(maxsize=None)
def load_prompt(name: str, attr: str = "PROMPT") -> str:
    """
    Import `constants.prompts.<name>` and return the string held in `attr`.

    Parameters
    ----------
    name : str
        The name of the prompt module to import.
    attr : str
        The attribute name to retrieve from the module.

    Returns
    -------
    str
        The prompt string.

    Raises
    ------
    ValueError
        If the module does not export the specified attribute.
    TypeError
        If the attribute is not a string or dict.
    """
    module = importlib.import_module(f"{_PACKAGE}.{name}")
    try:
        prompt_obj: Any = getattr(module, attr)
    except AttributeError as err:
        raise ValueError(
            f"Module '{name}' does not export '{attr}'."
        ) from err  # noqa: WPS237

    # Allow dict‑style collections
    if isinstance(prompt_obj, str):
        return prompt_obj
    raise TypeError(
        f"Module '{name}' does not export a string or dict. Got {type(prompt_obj)}."  # noqa: WPS237
    )


class OpenAIClient:
    """Encapsulates the OpenAI API client."""

    def __init__(self, api_key: str):
        """
        Initialize the OpenAIClient class with the API key.

        Raises:
            ValueError: If the OPENAI_API_KEY environment variable is not set.
        """
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def ask(self, messages: list, model: str = "gpt-4o", temperature: float = 0) -> str:
        """
        Ask a question to the OpenAI API.

        Args:
            messages (list): A list of messages in the conversation.
            model (str): The model to use for completion.
            temperature (float): The sampling temperature.

        Returns:
            str: The response from the OpenAI API.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        response = requests.post(
            self.base_url, headers=self.headers, json=payload, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def run_prompt(
        self,
        prompt_name: str,
        model: str = "gpt-4o",
        temperature: float = 0,
        attr: str = "PROMPT",
        **template_vars: Any,
    ) -> str:
        """
        Render a stored prompt template and send it.

        Example
        -------
        client.run_prompt(
            "summarization",
            transcribed_and_diarized=conversation_text
        )
        """
        template = load_prompt(prompt_name, attr=attr)
        rendered = template.format(**template_vars)

        if rendered.lstrip().startswith("System Message:"):
            system, user = rendered.split("User Message:", 1)
            messages = [
                {
                    "role": "system",
                    "content": system.replace("System Message:", "").strip(),
                },
                {"role": "user", "content": user.strip()},
            ]
        else:
            messages = [{"role": "user", "content": rendered}]

        return self.ask(messages=messages, model=model, temperature=temperature)

    @staticmethod
    def parse_response(raw_response: str) -> dict:
        """
        Parse OpenAI's response, clean code block markers, and convert to JSON.

        Parameters
        ----------
        raw_response : str
            The raw response from OpenAI.

        Returns
        -------
        dict
            Parsed JSON dictionary.

        Raises
        ------
        ValueError
            If JSON decoding fails or required keys are missing.
        """
        lines = raw_response.splitlines()
        json_lines = [line for line in lines if not line.startswith("```")]

        json_str = "\n".join(json_lines)

        try:
            summary_dict = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

        # Validate required keys
        required_keys = [
            "reason",
            "description",
            "products",
            "satisfaction",
            "fup",
            "tone_of_voice",
            "tags",
        ]
        for key in required_keys:
            if key not in summary_dict:
                raise ValueError(f"Missing expected key in summary: '{key}'")

        return summary_dict
