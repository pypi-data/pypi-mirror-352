
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pii.pii import analyze_and_mask_text
from toxicity.toxic_bert import detect_toxicity
from prompt_secure.prompt_break import classify_prompt_injection
import asyncio


app = FastAPI(
    title="LLM Guardrails Server",
    description="Request/Response Guard rails",
    version="1.0.0"
)


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


@app.get("/api/v1/guardrails")
async def list_guardrails():
    """List all available guardrails and their capabilities."""
    return {"guardrails": 123}


@app.post("/api/v1/toxicity")
async def validate_content(request: ToxiRequest):
    """Validate content against specified guardrails."""
    result = await detect_toxicity(request.content, request.treshold)
    return result


@app.post("/api/v1/mask_pii")
async def transform_content(request: TransformRequest):
    """Transform content using specified guardrails."""
    res = await analyze_and_mask_text(
        request.content, request.guardrails, request.custom_entities, request.treshold)
    return res


@app.post("/api/v1/prompt_injection")
async def prompt_injection(request: Prompt):
    """Detect prompt injection attempts."""
    result = await classify_prompt_injection(request.content)
    return result


@app.post("/api/v1/run_all_guardrails")
async def run_all_guardrails(request: TransformRequest):
    """Run all guardrails on the content."""
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


@app.get("/health")
async def health_check():
    """Health check."""
    # Check if all registered guardrails are properly initialized

    return "success"
