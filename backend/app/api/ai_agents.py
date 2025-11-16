"""
AI Agents API - Multi-AI Integration Endpoints

Provides REST API endpoints for invoking multiple AI systems.

Endpoints:
- POST /api/ai/gemini - Invoke Google Gemini
- POST /api/ai/openai - Invoke OpenAI (ChatGPT)
- POST /api/ai/claude - Invoke Anthropic Claude API
- POST /api/ai/cli - Invoke local CLI tools
- POST /api/ai/batch - Invoke multiple AIs in batch
- GET /api/ai/health - Health check of all AI providers

Usage:
    # Generate code with Gemini
    POST /api/ai/gemini
    {
        "prompt": "Generate FastAPI endpoint for candidates..."
    }

    # Review code with OpenAI
    POST /api/ai/openai
    {
        "prompt": "Review this code...",
        "system_message": "You are a code reviewer..."
    }

    # Batch invoke multiple AIs
    POST /api/ai/batch
    {
        "tasks": [
            {"provider": "gemini", "prompt": "..."},
            {"provider": "openai", "prompt": "..."}
        ]
    }
"""

import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.core.rate_limiter import limiter, RateLimitConfig
from app.services.ai_gateway import AIGateway, AIGatewayError
from app.models.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai-agents"])


# Request/Response schemas
class GeminiRequest(BaseModel):
    """Request schema for Gemini invocation"""
    prompt: str = Field(..., description="User prompt/instruction")
    max_tokens: int = Field(4096, description="Maximum tokens in response")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Model temperature")
    system_instruction: Optional[str] = Field(None, description="System instruction")


class OpenAIRequest(BaseModel):
    """Request schema for OpenAI invocation"""
    prompt: str = Field(..., description="User prompt/instruction")
    model: str = Field("gpt-4-turbo-preview", description="Model name")
    max_tokens: int = Field(4096, description="Maximum tokens in response")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Model temperature")
    system_message: Optional[str] = Field(None, description="System message")


class ClaudeAPIRequest(BaseModel):
    """Request schema for Claude API invocation"""
    prompt: str = Field(..., description="User prompt/instruction")
    model: str = Field("claude-3-5-sonnet-20241022", description="Model name")
    max_tokens: int = Field(4096, description="Maximum tokens in response")
    system_prompt: Optional[str] = Field(None, description="System prompt")


class LocalCLIRequest(BaseModel):
    """Request schema for local CLI tool invocation"""
    tool: str = Field(..., description="Tool name (e.g., 'gemini-cli')")
    args: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    timeout: int = Field(60, description="Process timeout in seconds")


class BatchTask(BaseModel):
    """Task for batch invocation"""
    provider: str = Field(..., description="AI provider: gemini|openai|claude_api|local_cli")
    prompt: Optional[str] = Field(None, description="User prompt")
    tool: Optional[str] = Field(None, description="Tool name (for local_cli)")
    args: Optional[Dict[str, Any]] = Field(None, description="Arguments")
    max_tokens: Optional[int] = Field(4096, description="Max tokens")
    temperature: Optional[float] = Field(0.7, description="Temperature")
    model: Optional[str] = Field(None, description="Model name")
    system_instruction: Optional[str] = Field(None, description="System instruction")
    system_message: Optional[str] = Field(None, description="System message")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    timeout: Optional[int] = Field(60, description="Timeout (CLI tools)")


class BatchRequest(BaseModel):
    """Request schema for batch invocation"""
    tasks: List[BatchTask] = Field(..., description="List of AI tasks")
    parallel: bool = Field(True, description="Execute in parallel")


class AIResponse(BaseModel):
    """Response schema for AI invocations"""
    status: str = Field(..., description="Response status: success|error")
    provider: str = Field(..., description="AI provider used")
    response: Optional[str] = Field(None, description="AI response")
    error: Optional[str] = Field(None, description="Error message (if failed)")
    tokens_used: Optional[int] = Field(None, description="Tokens used (if applicable)")


class BatchResponse(BaseModel):
    """Response schema for batch invocation"""
    status: str = Field(..., description="Overall status: success|partial|error")
    results: List[Dict[str, Any]] = Field(..., description="Results from each task")
    total_tasks: int = Field(..., description="Total tasks executed")
    successful: int = Field(..., description="Number of successful tasks")
    failed: int = Field(..., description="Number of failed tasks")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Overall status: healthy|degraded|unhealthy")
    providers: Dict[str, str] = Field(..., description="Status of each provider")


# Dependency to get AI Gateway
async def get_ai_gateway() -> AIGateway:
    """Get AI Gateway instance"""
    return AIGateway()


# Endpoints
@router.post("/gemini", response_model=AIResponse)
@limiter.limit(RateLimitConfig.GEMINI_LIMIT)
@limiter.limit(RateLimitConfig.GEMINI_BURST)
async def invoke_gemini(
    request: GeminiRequest,
    gateway: AIGateway = Depends(get_ai_gateway),
    current_user: User = Depends(get_current_user),
) -> AIResponse:
    """
    Invoke Google Gemini for code generation or analysis.

    Requires authentication. Limited by rate limits and quota.

    Args:
        request: Gemini request parameters
        gateway: AI Gateway instance
        current_user: Current authenticated user

    Returns:
        AIResponse with Gemini's generated text

    Raises:
        HTTPException: If invocation fails
    """
    try:
        logger.info(f"User {current_user.username} invoking Gemini")

        response = await gateway.invoke_gemini(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system_instruction=request.system_instruction,
        )

        return AIResponse(
            status="success",
            provider="gemini",
            response=response,
        )

    except AIGatewayError as e:
        logger.error(f"Gemini invocation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gemini invocation failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error invoking Gemini: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/openai", response_model=AIResponse)
@limiter.limit(RateLimitConfig.OPENAI_LIMIT)
@limiter.limit(RateLimitConfig.OPENAI_BURST)
async def invoke_openai(
    request: OpenAIRequest,
    gateway: AIGateway = Depends(get_ai_gateway),
    current_user: User = Depends(get_current_user),
) -> AIResponse:
    """
    Invoke OpenAI (ChatGPT) for analysis, review, or architecture.

    Requires authentication. Limited by API quota and rate limits.

    Args:
        request: OpenAI request parameters
        gateway: AI Gateway instance
        current_user: Current authenticated user

    Returns:
        AIResponse with OpenAI's response

    Raises:
        HTTPException: If invocation fails
    """
    try:
        logger.info(f"User {current_user.username} invoking OpenAI")

        response = await gateway.invoke_openai(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system_message=request.system_message,
        )

        return AIResponse(
            status="success",
            provider="openai",
            response=response,
        )

    except AIGatewayError as e:
        logger.error(f"OpenAI invocation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OpenAI invocation failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error invoking OpenAI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/claude", response_model=AIResponse)
@limiter.limit(RateLimitConfig.CLAUDE_API_LIMIT)
@limiter.limit(RateLimitConfig.CLAUDE_API_BURST)
async def invoke_claude_api(
    request: ClaudeAPIRequest,
    gateway: AIGateway = Depends(get_ai_gateway),
    current_user: User = Depends(get_current_user),
) -> AIResponse:
    """
    Invoke Anthropic Claude API (external).

    Note: This is the external Claude API service, not Claude Code.
    Requires authentication and API quota.

    Args:
        request: Claude API request parameters
        gateway: AI Gateway instance
        current_user: Current authenticated user

    Returns:
        AIResponse with Claude's response

    Raises:
        HTTPException: If invocation fails
    """
    try:
        logger.info(f"User {current_user.username} invoking Claude API")

        response = await gateway.invoke_claude_api(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt,
        )

        return AIResponse(
            status="success",
            provider="claude_api",
            response=response,
        )

    except AIGatewayError as e:
        logger.error(f"Claude API invocation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Claude API invocation failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error invoking Claude API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/cli", response_model=AIResponse)
@limiter.limit(RateLimitConfig.LOCAL_CLI_LIMIT)
@limiter.limit(RateLimitConfig.LOCAL_CLI_BURST)
async def invoke_local_cli(
    request: LocalCLIRequest,
    gateway: AIGateway = Depends(get_ai_gateway),
    current_user: User = Depends(get_current_user),
) -> AIResponse:
    """
    Invoke local CLI tool (gemini-cli, custom tools, etc.).

    Useful for integrating local development tools with the API.

    Args:
        request: CLI request parameters
        gateway: AI Gateway instance
        current_user: Current authenticated user

    Returns:
        AIResponse with CLI tool output

    Raises:
        HTTPException: If tool execution fails
    """
    try:
        logger.info(f"User {current_user.username} invoking local CLI: {request.tool}")

        response = await gateway.invoke_local_cli(
            tool=request.tool,
            args=request.args,
            timeout=request.timeout,
        )

        return AIResponse(
            status="success",
            provider="local_cli",
            response=response,
        )

    except AIGatewayError as e:
        logger.error(f"CLI invocation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CLI invocation failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error invoking CLI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/batch", response_model=BatchResponse)
@limiter.limit(RateLimitConfig.BATCH_LIMIT)
async def batch_invoke(
    request: BatchRequest,
    gateway: AIGateway = Depends(get_ai_gateway),
    current_user: User = Depends(get_current_user),
) -> BatchResponse:
    """
    Invoke multiple AI systems in parallel or sequence.

    Useful for coordinating responses from multiple AI providers.

    Args:
        request: Batch request with list of tasks
        gateway: AI Gateway instance
        current_user: Current authenticated user

    Returns:
        BatchResponse with results from all tasks

    Example:
        {
            "tasks": [
                {
                    "provider": "gemini",
                    "prompt": "Generate FastAPI endpoint..."
                },
                {
                    "provider": "openai",
                    "prompt": "Review the generated code..."
                }
            ]
        }
    """
    try:
        logger.info(
            f"User {current_user.username} invoking batch with {len(request.tasks)} tasks"
        )

        results = await gateway.batch_invoke(
            tasks=[task.dict() for task in request.tasks],
            parallel=request.parallel,
        )

        # Count successes and failures
        successful = sum(1 for r in results if r.get("status") == "success")
        failed = sum(1 for r in results if r.get("status") == "error")

        # Determine overall status
        if failed == 0:
            overall_status = "success"
        elif successful == 0:
            overall_status = "error"
        else:
            overall_status = "partial"

        return BatchResponse(
            status=overall_status,
            results=results,
            total_tasks=len(results),
            successful=successful,
            failed=failed,
        )

    except Exception as e:
        logger.error(f"Batch invocation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch invocation failed"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(
    gateway: AIGateway = Depends(get_ai_gateway),
) -> HealthResponse:
    """
    Check health status of all AI providers.

    Returns:
        HealthResponse with status of each configured provider

    Example response:
        {
            "status": "healthy",
            "providers": {
                "gemini": "healthy",
                "openai": "healthy",
                "claude_api": "not_configured",
                "local_cli": "available"
            }
        }
    """
    try:
        health = await gateway.health_check()

        # Determine overall health
        provider_statuses = list(health.get("providers", {}).values())
        unhealthy_count = sum(
            1 for s in provider_statuses if "unhealthy" in s.lower() or "error" in s.lower()
        )

        if unhealthy_count == 0:
            overall_status = "healthy"
        elif unhealthy_count < len(provider_statuses):
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        return HealthResponse(
            status=overall_status,
            providers=health.get("providers", {}),
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )
