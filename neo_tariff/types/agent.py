"""Agent response models.

Used by ``client.agent.chat()``, ``client.agent.get_trace()``, etc.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Nested models
# ---------------------------------------------------------------------------


class AgentCitation(BaseModel):
    """A citation referencing a data source used in the agent response."""

    model_config = ConfigDict(extra="allow")

    type: str | None = Field(
        default=None,
        description="Citation type (e.g. hts_code, note, ch99_rule, country).",
    )
    id: str | None = Field(
        default=None, description="Identifier (e.g. HTS code, note ID, country ISO)."
    )
    label: str | None = Field(default=None, description="Human-readable short label.")
    nav_link: str | None = Field(default=None, description="Frontend navigation link.")


class AgentToolCall(BaseModel):
    """Record of a tool call made by the agent during reasoning."""

    model_config = ConfigDict(extra="allow")

    tool_name: str | None = Field(default=None, description="Name of the tool invoked.")
    arguments: dict[str, Any] | None = Field(
        default=None, description="Arguments passed to the tool."
    )
    success: bool | None = Field(
        default=None, description="Whether the tool call succeeded."
    )
    error: str | None = Field(
        default=None, description="Error message if the call failed."
    )
    error_code: str | None = Field(
        default=None,
        description="Categorized error type (e.g. timeout, validation_error).",
    )
    retryable: bool | None = Field(
        default=None, description="Whether the failed call may succeed on retry."
    )
    duration_ms: float | None = Field(
        default=None, description="Execution duration in milliseconds."
    )


class AgentResponseMetadata(BaseModel):
    """Metadata about the agent's response generation."""

    model_config = ConfigDict(extra="allow")

    model: str | None = Field(default=None, description="LLM model used.")
    total_tokens: int | None = Field(default=None, description="Total tokens consumed.")
    prompt_tokens: int | None = Field(
        default=None, description="Prompt tokens consumed."
    )
    completion_tokens: int | None = Field(
        default=None, description="Completion tokens consumed."
    )
    tool_calls_count: int | None = Field(
        default=None, description="Number of tool calls made."
    )
    tool_iterations: int | None = Field(
        default=None, description="Number of agent loop iterations."
    )
    latency_ms: float | None = Field(
        default=None, description="Total response latency in milliseconds."
    )
    hts_year: int | None = Field(default=None, description="HTS revision year used.")
    hts_version: int | None = Field(
        default=None, description="HTS revision version used."
    )
    request_id: str | None = Field(
        default=None, description="Server-assigned request identifier."
    )
    conversation_persistence: str | None = Field(
        default=None, description="Persistence mode (redis or stateless)."
    )


# ---------------------------------------------------------------------------
# Chat response
# ---------------------------------------------------------------------------


class AgentChatResponse(BaseModel):
    """Response from the ``POST /agent/chat`` endpoint."""

    model_config = ConfigDict(extra="allow")

    conversation_id: str | None = Field(
        default=None, description="Conversation thread ID (reuse for follow-ups)."
    )
    response: str | None = Field(
        default=None, description="Agent's natural language response."
    )
    citations: list[AgentCitation] | None = Field(
        default=None, description="Sources referenced in the response."
    )
    tools_used: list[AgentToolCall] | None = Field(
        default=None, description="Tool calls made during reasoning."
    )
    metadata: AgentResponseMetadata | None = Field(
        default=None, description="Response generation metadata."
    )
    disclaimer: str | None = Field(
        default=None, description="Legal disclaimer (always included)."
    )
    turn_id: str | None = Field(
        default=None,
        description="Turn identifier for trace retrieval (format: turn_{hex}).",
    )
    explain_steps: list[str] | None = Field(
        default=None, description="Human-readable step summaries (when requested)."
    )
    trace_available: bool | None = Field(
        default=None, description="Whether the full execution trace was persisted."
    )


# ---------------------------------------------------------------------------
# Trace models
# ---------------------------------------------------------------------------


class AgentTraceStep(BaseModel):
    """One tool execution within an agent turn."""

    model_config = ConfigDict(extra="allow")

    iteration: int | None = Field(
        default=None, description="Agent loop iteration (1-indexed)."
    )
    tool_name: str | None = Field(default=None, description="Name of the tool invoked.")
    arguments: dict[str, Any] | None = Field(
        default=None, description="Arguments passed to the tool."
    )
    compressed_result: Any | None = Field(
        default=None, description="Compressed tool result (same shape returned to LLM)."
    )
    status: str | None = Field(
        default=None, description="Execution status (success or error)."
    )
    error_code: str | None = Field(default=None, description="Categorized error type.")
    error_message: str | None = Field(
        default=None, description="Error message if the step failed."
    )
    retryable: bool | None = Field(
        default=None, description="Whether the failed step may succeed on retry."
    )
    duration_ms: float | None = Field(
        default=None, description="Execution duration in milliseconds."
    )
    assistant_reasoning: str | None = Field(
        default=None, description="LLM intermediate reasoning for this iteration."
    )


class AgentTrace(BaseModel):
    """Full execution trace for a single agent turn."""

    model_config = ConfigDict(extra="allow")

    trace_id: str | None = Field(default=None, description="Unique trace identifier.")
    turn_id: str | None = Field(
        default=None, description="Turn identifier (format: turn_{hex})."
    )
    conversation_id: str | None = Field(
        default=None, description="Conversation the turn belongs to."
    )
    owner_scope_hash: str | None = Field(
        default=None, description="Hashed owner scope for privacy."
    )
    steps: list[AgentTraceStep] | None = Field(
        default=None, description="Ordered list of tool execution steps."
    )
    total_iterations: int | None = Field(
        default=None, description="Total agent loop iterations."
    )
    total_tool_calls: int | None = Field(
        default=None, description="Total tool calls across all iterations."
    )
    total_duration_ms: float | None = Field(
        default=None, description="Total execution duration in milliseconds."
    )
    created_at: str | None = Field(
        default=None, description="ISO 8601 creation timestamp."
    )


# ---------------------------------------------------------------------------
# Context model (used as input)
# ---------------------------------------------------------------------------


class AgentContext(BaseModel):
    """Optional context about what the user is currently viewing or working with.

    Pass this to ``client.agent.chat(context=...)`` to pin contextual
    information across the conversation.
    """

    model_config = ConfigDict(extra="allow")

    hts_code: str | None = Field(default=None, description="HTS code user is viewing.")
    chapter_number: int | None = Field(
        default=None, description="Chapter number (1-99)."
    )
    section_number: int | None = Field(
        default=None, description="Section number (1-22)."
    )
    country_of_origin: str | None = Field(
        default=None, description="Country name or ISO code."
    )
    customs_value: float | None = Field(
        default=None, description="Customs value in USD."
    )
    quantity: float | None = Field(default=None, description="Quantity.")
    import_date: str | None = Field(
        default=None, description="Import date (YYYY-MM-DD)."
    )


# ---------------------------------------------------------------------------
# Delete conversation response
# ---------------------------------------------------------------------------


class DeleteConversationResponse(BaseModel):
    """Response from the ``DELETE /agent/conversations/{id}`` endpoint."""

    model_config = ConfigDict(extra="allow")

    deleted: bool | None = Field(
        default=None, description="Whether the conversation was deleted."
    )
    conversation_id: str | None = Field(
        default=None, description="ID of the conversation that was deleted."
    )
