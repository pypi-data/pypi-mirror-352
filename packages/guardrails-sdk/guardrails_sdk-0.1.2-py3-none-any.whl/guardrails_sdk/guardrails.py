from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .pii.pii import analyze_and_mask_text
from .toxicity.toxic_bert import detect_toxicity
from .prompt_secure.prompt_break import classify_prompt_injection
import asyncio


class ToxiRequest(BaseModel):
    content: str
    treshold: float = 0.5


class Prompt(BaseModel):
    content: str


class TransformRequest(BaseModel):
    content: str
    guardrails: List[str]
    treshold: float = 0.5
    custom_entities: Optional[List[Dict]] = None


class GuardrailsClient:
    def __init__(self):
        pass

    async def validate_content(self, request: ToxiRequest):
        result = await detect_toxicity(request.content, request.treshold)
        return result

    async def transform_content(self, request: TransformRequest):
        res = await analyze_and_mask_text(
            request.content, request.guardrails, request.custom_entities, request.treshold)
        return res

    async def prompt_injection(self, request: Prompt):
        result = await classify_prompt_injection(request.content)
        return result

    async def run_all_guardrails(self, request: TransformRequest):
        pii_result, toxicity_result, prompt_injection_result = await asyncio.gather(
            analyze_and_mask_text(
                request.content, request.guardrails, request.custom_entities, request.treshold),
            detect_toxicity(request.content, request.treshold),
            classify_prompt_injection(request.content)
        )
        return {
            "pii": pii_result,
            "toxicity": toxicity_result,
            "prompt_injection": prompt_injection_result
        }
