"""The AI models Liasse uses. The only module that talks to an LLM; tests replace it with a fake."""

import json
import re
from datetime import date
from typing import Protocol

import litellm
from pydantic import BaseModel, Field, ValidationError

from liasse.settings import Settings

# Classification reads the start of a Document; that's where sender, date and subject are.
CLASSIFY_MAX_CHARS = 12_000


class Classification(BaseModel):
    category: str | None
    category_confidence: float = Field(ge=0, le=1)
    correspondent: str | None
    correspondent_confidence: float = Field(ge=0, le=1)
    document_date: date | None
    document_date_confidence: float = Field(ge=0, le=1)
    title: str = Field(min_length=1, max_length=80)


class InvalidModelOutput(ValueError):
    """The model answered something Liasse can't use."""


class Models(Protocol):
    def classify(
        self, text: str, categories: list[str], correspondents: list[str]
    ) -> Classification: ...


CLASSIFY_PROMPT = """You file paper documents for one person. Read the document text below \
(from OCR, so it may contain mistakes) and decide:

- category: exactly one of {categories}, or null if none fits.
- correspondent: who sent or issued the document (a company, administration or person). \
If it is one of these existing correspondents, return that exact name: {correspondents}. \
Otherwise return a short, common name for it (e.g. "EDF", not "Électricité de France SA").
- document_date: the date printed on the document (issue date), as YYYY-MM-DD, or null.
- title: a short title in the document's language, 2 to 6 words, without the correspondent \
or the date (e.g. "Facture électricité", "Payslip").
- a confidence between 0 and 1 for category, correspondent and document_date. Use a low \
confidence when you are guessing.

Answer with only this JSON object, nothing else:
{{"category": ..., "category_confidence": ..., "correspondent": ..., \
"correspondent_confidence": ..., "document_date": ..., "document_date_confidence": ..., \
"title": ...}}

Document text:
<document>
{text}
</document>"""


def parse_classification(answer: str) -> Classification:
    """Read the JSON object out of a model's answer, tolerating code fences or a preamble."""
    match = re.search(r"\{.*\}", answer, re.DOTALL)
    if match is None:
        raise InvalidModelOutput("The model didn't return a classification.")
    try:
        return Classification.model_validate(json.loads(match.group()))
    except (json.JSONDecodeError, ValidationError):
        raise InvalidModelOutput("The model's classification couldn't be read.") from None


class LiteLLMModels:
    """Calls whichever provider LLM_MODEL names: anthropic/…, openai/… or ollama/…."""

    def __init__(self, settings: Settings) -> None:
        if not settings.llm_model:
            raise SystemExit(
                "Liasse cannot process Documents: LLM_MODEL is not set. "
                "See .env.example for Claude, OpenAI and Ollama examples."
            )
        self.model = settings.llm_model
        # Empty values from .env mean "not set", so LiteLLM falls back to its own env variables.
        self.api_key = (
            settings.llm_api_key.get_secret_value() if settings.llm_api_key else ""
        ) or None
        self.api_base = settings.llm_api_base or None

    def classify(
        self, text: str, categories: list[str], correspondents: list[str]
    ) -> Classification:
        prompt = CLASSIFY_PROMPT.format(
            categories=json.dumps(categories, ensure_ascii=False),
            correspondents=json.dumps(correspondents, ensure_ascii=False)
            if correspondents
            else "none yet",
            text=text[:CLASSIFY_MAX_CHARS],
        )
        # No temperature or JSON mode: some models reject them; the prompt and parser suffice.
        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            api_key=self.api_key,
            api_base=self.api_base,
        )
        return parse_classification(response.choices[0].message.content or "")
