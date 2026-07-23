"""
target.py

Handles the connection to whatever AI system Warden is testing.
Supports multiple providers behind one common interface, so the rest
of Warden (runner, evaluator, report) never needs to know which
provider is actually being tested.
"""

import os
from abc import ABC, abstractmethod


class Target(ABC):
    """Base class for any AI system Warden can test."""

    @abstractmethod
    def send(self, prompt: str) -> str:
        """Send a single prompt to the target and return its text response."""
        raise NotImplementedError


class AnthropicTarget(Target):
    """Target adapter for Claude (Anthropic API)."""

    def __init__(self, model: str = "claude-sonnet-4-6", api_key: str | None = None):
        try:
            import anthropic
        except ImportError as e:
            raise ImportError(
                "The 'anthropic' package is required for AnthropicTarget. "
                "Install it with: pip install anthropic"
            ) from e

        self.model = model
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError(
                "No Anthropic API key found. Set the ANTHROPIC_API_KEY "
                "environment variable or pass api_key explicitly."
            )
        self.client = anthropic.Anthropic(api_key=key)

    def send(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        # Concatenate all text blocks in the response
        return "".join(
            block.text for block in response.content if block.type == "text"
        )


class OpenAITarget(Target):
    """Target adapter for GPT models (OpenAI API)."""

    def __init__(self, model: str = "gpt-4o", api_key: str | None = None):
        try:
            import openai
        except ImportError as e:
            raise ImportError(
                "The 'openai' package is required for OpenAITarget. "
                "Install it with: pip install openai"
            ) from e

        self.model = model
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError(
                "No OpenAI API key found. Set the OPENAI_API_KEY "
                "environment variable or pass api_key explicitly."
            )
        self.client = openai.OpenAI(api_key=key)

    def send(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


class MockTarget(Target):
    """
    A fake target that needs no API key at all.

    Useful for building and testing the rest of Warden's pipeline
    (payloads, runner, evaluator, report) before wiring up a real
    AI system. It echoes the prompt back with a canned reply so
    you can verify the plumbing works end to end.
    """

    def __init__(self, canned_response: str = "I cannot help with that request."):
        self.canned_response = canned_response

    def send(self, prompt: str) -> str:
        return self.canned_response


def get_target(provider: str, **kwargs) -> Target:
    """
    Factory function: returns the right Target implementation by name.

    provider: "anthropic", "openai", or "mock"
    """
    providers = {
        "anthropic": AnthropicTarget,
        "openai": OpenAITarget,
        "mock": MockTarget,
    }
    if provider not in providers:
        raise ValueError(
            f"Unknown provider '{provider}'. Choose from: {list(providers.keys())}"
        )
    return providers[provider](**kwargs)
