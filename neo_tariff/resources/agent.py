"""Agent resource – Tariff Intelligence Agent endpoints."""

from __future__ import annotations

from typing import Any

from neo_tariff._http import _clean
from neo_tariff._types import APIResponse
from neo_tariff.resources._base import AsyncResource, SyncResource
from neo_tariff.types.agent import (
    AgentChatResponse,
    AgentContext,
    AgentTrace,
    DeleteConversationResponse,
)


class AgentResource(SyncResource):
    """Synchronous agent resource."""

    def chat(
        self,
        *,
        message: str,
        conversation_id: str | None = None,
        context: AgentContext | dict[str, Any] | None = None,
        history: list[dict[str, str]] | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
        include_explain_steps: bool = False,
    ) -> APIResponse[AgentChatResponse]:
        """Send a message to the Tariff Intelligence Agent.

        Supports multi-turn conversations via ``conversation_id``.  Omit
        ``conversation_id`` to start a new conversation; include it to
        continue an existing thread.

        Calls ``POST /agent/chat``.

        Parameters
        ----------
        message:
            User's question or message (1-4000 characters).
        conversation_id:
            Existing conversation ID for multi-turn continuity.
        context:
            Optional context about the user's current view (HTS code,
            country, customs value, etc.).  Can be an ``AgentContext``
            instance or a plain dict.
        history:
            Conversation history (list of ``{"role": ..., "content": ...}``
            dicts).  Used only when ``conversation_id`` is not provided.
        hts_year:
            HTS revision year override.
        hts_version:
            HTS revision version override.
        include_explain_steps:
            When ``True``, the response includes human-readable step-by-step
            explanation of tool calls in ``explain_steps``.
        """
        ctx = None
        if context is not None:
            ctx = (
                context.model_dump(mode="json", exclude_none=True)
                if isinstance(context, AgentContext)
                else context
            )

        body = _clean(
            {
                "message": message,
                "conversation_id": conversation_id,
                "context": ctx,
                "history": history,
                "hts_year": hts_year,
                "hts_version": hts_version,
                "include_explain_steps": include_explain_steps or None,
            }
        )
        return self._http.request_typed(
            "POST",
            "/agent/chat",
            json_body=body,
            response_type=AgentChatResponse,
        )

    def delete_conversation(
        self,
        conversation_id: str,
    ) -> APIResponse[DeleteConversationResponse]:
        """Delete an agent conversation thread.

        Removes the conversation from Redis.  This is irreversible.

        Calls ``DELETE /agent/conversations/{conversation_id}``.

        Parameters
        ----------
        conversation_id:
            The conversation thread ID to delete.
        """
        return self._http.request_typed(
            "DELETE",
            f"/agent/conversations/{conversation_id}",
            response_type=DeleteConversationResponse,
        )

    def get_trace(
        self,
        turn_id: str,
        *,
        conversation_id: str,
    ) -> APIResponse[AgentTrace]:
        """Retrieve the full execution trace for a specific agent turn.

        Returns the detailed tool execution trace including tool arguments,
        compressed results, durations, and the LLM's intermediate reasoning.
        Traces are available for 24 hours after creation.

        This endpoint is **not metered** — the work was already billed on the
        original ``chat()`` call.

        Calls ``GET /agent/traces/{turn_id}``.

        Parameters
        ----------
        turn_id:
            The turn identifier from the chat response (format: ``turn_{hex}``).
        conversation_id:
            The conversation the turn belongs to.
        """
        return self._http.request_typed(
            "GET",
            f"/agent/traces/{turn_id}",
            params={"conversation_id": conversation_id},
            response_type=AgentTrace,
        )


class AsyncAgentResource(AsyncResource):
    """Asynchronous agent resource."""

    async def chat(
        self,
        *,
        message: str,
        conversation_id: str | None = None,
        context: AgentContext | dict[str, Any] | None = None,
        history: list[dict[str, str]] | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
        include_explain_steps: bool = False,
    ) -> APIResponse[AgentChatResponse]:
        """Send a message to the Tariff Intelligence Agent.

        Supports multi-turn conversations via ``conversation_id``.  Omit
        ``conversation_id`` to start a new conversation; include it to
        continue an existing thread.

        Calls ``POST /agent/chat``.

        Parameters
        ----------
        message:
            User's question or message (1-4000 characters).
        conversation_id:
            Existing conversation ID for multi-turn continuity.
        context:
            Optional context about the user's current view (HTS code,
            country, customs value, etc.).  Can be an ``AgentContext``
            instance or a plain dict.
        history:
            Conversation history (list of ``{"role": ..., "content": ...}``
            dicts).  Used only when ``conversation_id`` is not provided.
        hts_year:
            HTS revision year override.
        hts_version:
            HTS revision version override.
        include_explain_steps:
            When ``True``, the response includes human-readable step-by-step
            explanation of tool calls in ``explain_steps``.
        """
        ctx = None
        if context is not None:
            ctx = (
                context.model_dump(mode="json", exclude_none=True)
                if isinstance(context, AgentContext)
                else context
            )

        body = _clean(
            {
                "message": message,
                "conversation_id": conversation_id,
                "context": ctx,
                "history": history,
                "hts_year": hts_year,
                "hts_version": hts_version,
                "include_explain_steps": include_explain_steps or None,
            }
        )
        return await self._http.request_typed(
            "POST",
            "/agent/chat",
            json_body=body,
            response_type=AgentChatResponse,
        )

    async def delete_conversation(
        self,
        conversation_id: str,
    ) -> APIResponse[DeleteConversationResponse]:
        """Delete an agent conversation thread.

        Removes the conversation from Redis.  This is irreversible.

        Calls ``DELETE /agent/conversations/{conversation_id}``.

        Parameters
        ----------
        conversation_id:
            The conversation thread ID to delete.
        """
        return await self._http.request_typed(
            "DELETE",
            f"/agent/conversations/{conversation_id}",
            response_type=DeleteConversationResponse,
        )

    async def get_trace(
        self,
        turn_id: str,
        *,
        conversation_id: str,
    ) -> APIResponse[AgentTrace]:
        """Retrieve the full execution trace for a specific agent turn.

        Returns the detailed tool execution trace including tool arguments,
        compressed results, durations, and the LLM's intermediate reasoning.
        Traces are available for 24 hours after creation.

        This endpoint is **not metered** — the work was already billed on the
        original ``chat()`` call.

        Calls ``GET /agent/traces/{turn_id}``.

        Parameters
        ----------
        turn_id:
            The turn identifier from the chat response (format: ``turn_{hex}``).
        conversation_id:
            The conversation the turn belongs to.
        """
        return await self._http.request_typed(
            "GET",
            f"/agent/traces/{turn_id}",
            params={"conversation_id": conversation_id},
            response_type=AgentTrace,
        )
