# tests/test_openai_client.py
import pytest
import json as jsonlib

from o2_speechless.llm.provider.openai.client import OpenAIClient


def mock_openai_json(content: str) -> dict:
    """Return the minimal JSON envelope the OpenAI chat endpoint sends back."""
    return {"choices": [{"message": {"content": content}}]}


@pytest.fixture
def fake_post(monkeypatch):
    """Patch requests.post so no real network traffic occurs."""

    import requests  # Import requests here to avoid circular import issues

    def _fake_post(url, headers, json=None, timeout=None):
        class _Resp:
            status_code = 200

            @staticmethod
            def raise_for_status():
                pass

            @staticmethod
            def json():
                payload = {
                    "reason": "help_with_checkout",
                    "description": "Agent fixed payment error.",
                    "products": ["premium_plan"],
                    "satisfaction": "positive",
                    "fup": False,
                    "tone_of_voice": [],
                    "tags": ["checkout", "payment"],
                }
                return mock_openai_json(jsonlib.dumps(payload))

        return _Resp()

    monkeypatch.setattr(requests, "post", _fake_post)


def test_ask_returns_content(fake_post):
    client = OpenAIClient(api_key="SK-FAKE")
    msg = [{"role": "user", "content": "dummy"}]

    raw = client.ask(messages=msg)

    parsed = client.parse_response(raw)
    assert parsed["reason"] == "help_with_checkout"
    assert parsed["products"] == ["premium_plan"]
    assert parsed["fup"] is False


def test_run_prompt(fake_post, monkeypatch, tmp_path):
    """
    End‑to‑end test of run_prompt + prompt loader without a real API key.
    We simulate a prompt module at runtime to avoid touching disk.
    """

    pkg_root = tmp_path / "constants" / "prompts"
    pkg_root.mkdir(parents=True)
    (pkg_root.parent / "__init__.py").touch()
    (pkg_root / "__init__.py").touch()

    prompt_code = 'PROMPT = """System Message:\\nX\\n\\nUser Message:\\n{who}"""'
    (pkg_root / "summarization.py").write_text(prompt_code)

    import sys, importlib

    sys.path.insert(0, str(tmp_path))
    importlib.invalidate_caches()

    client = OpenAIClient(api_key="SK-FAKE")
    raw = client.run_prompt(
        "summarization", transcribed_and_diarized="some dummy content"
    )

    parsed = client.parse_response(raw)

    assert parsed["reason"] == "help_with_checkout"


def test_run_prompt_with_real_prompt(fake_post):
    """Test run_prompt using the actual summarization prompt from constants.prompts."""
    client = OpenAIClient(api_key="SK-FAKE")

    # Simulate a realistic transcript input
    dummy_transcript = (
        "Customer: I need help understanding my recent charges.\n"
        "Agent: Sure, I see you were billed for an upgrade to the premium plan.\n"
        "Customer: Oh, that makes sense now. Thanks!"
    )

    # Run the real summarization prompt using that transcript
    raw = client.run_prompt("summarization", transcribed_and_diarized=dummy_transcript)

    parsed = client.parse_response(raw)

    # Assert the mocked return values are parsed correctly
    assert isinstance(parsed, dict)
    assert parsed["reason"] == "help_with_checkout"
    assert parsed["satisfaction"] == "positive"
    assert parsed["products"] == ["premium_plan"]
    assert isinstance(parsed["tags"], list)
