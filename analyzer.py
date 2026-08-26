import json
import logging

from app.config import settings
from app.risk_engine.deterministic import analyze_deterministically
from app.schemas.risk import RiskAssessment

logger = logging.getLogger(__name__)


class AnalysisService:
    """Selects an analysis provider while keeping a deterministic offline path."""

    def analyze(self, text: str) -> RiskAssessment:
        if settings.risk_engine_mode.lower() != "llm" or not settings.openai_api_key:
            return analyze_deterministically(text)

        try:
            return self._analyze_with_llm(text)
        except Exception as exc:  # defensive: an unavailable provider must not break the MVP
            logger.warning("LLM analysis unavailable; using deterministic fallback: %s", exc)
            return analyze_deterministically(text)

    def _analyze_with_llm(self, text: str) -> RiskAssessment:
        from openai import OpenAI

        client_kwargs = {"api_key": settings.openai_api_key}
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url
        client = OpenAI(**client_kwargs)

        schema = RiskAssessment.model_json_schema()
        response = client.chat.completions.create(
            model=settings.openai_model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a cautious AI risk triage assistant. Return only JSON matching this schema. "
                        "Do not claim legal or certified compliance. Scores are 0-100. "
                        f"Schema: {json.dumps(schema)}"
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        content = response.choices[0].message.content or "{}"
        payload = json.loads(content)
        payload["engine"] = "llm"
        return RiskAssessment.model_validate(payload)


analysis_service = AnalysisService()
