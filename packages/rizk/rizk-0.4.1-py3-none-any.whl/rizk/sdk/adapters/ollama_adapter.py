"""
Ollama LLM Adapter for Rizk SDK

This adapter provides integration with Ollama API for LLM guardrails and observability.
It patches the Ollama client to inject guidelines and apply policy enforcement.
"""

import logging
from typing import Any, Dict, List, Optional, Callable

from rizk.sdk.adapters.llm_base_adapter import BaseLLMAdapter
from rizk.sdk.utils.error_handler import handle_errors

logger = logging.getLogger(__name__)

# Check if ollama is available
try:
    import ollama
    from ollama import Client, AsyncClient

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.debug("ollama not available, Ollama adapter will be disabled")


class OllamaAdapter(BaseLLMAdapter):
    """Adapter for Ollama API integration with Rizk SDK guardrails."""

    is_available = OLLAMA_AVAILABLE

    # Type annotations for original methods
    original_chat: Optional[Callable[..., Any]]
    original_chat_async: Optional[Callable[..., Any]]
    original_generate: Optional[Callable[..., Any]]
    original_generate_async: Optional[Callable[..., Any]]
    _patched: bool

    def __init__(self) -> None:
        super().__init__()
        self.original_chat = None
        self.original_chat_async = None
        self.original_generate = None
        self.original_generate_async = None
        self._patched = False

    def patch(self) -> None:
        """Patch Ollama client methods to inject guidelines."""
        if not OLLAMA_AVAILABLE:
            logger.debug("Ollama not available, skipping patching")
            return

        if self._patched:
            logger.debug("Ollama client already patched")
            return

        try:
            # Patch the global ollama functions
            if hasattr(ollama, "chat"):
                self.original_chat = ollama.chat
                ollama.chat = self._patched_chat

            if hasattr(ollama, "generate"):
                self.original_generate = ollama.generate
                ollama.generate = self._patched_generate

            # Patch Client methods
            if hasattr(Client, "chat"):
                Client._original_chat = Client.chat
                Client.chat = self._patched_client_chat

            if hasattr(Client, "generate"):
                Client._original_generate = Client.generate
                Client.generate = self._patched_client_generate

            # Patch AsyncClient methods
            if hasattr(AsyncClient, "chat"):
                AsyncClient._original_chat = AsyncClient.chat
                AsyncClient.chat = self._patched_async_client_chat

            if hasattr(AsyncClient, "generate"):
                AsyncClient._original_generate = AsyncClient.generate
                AsyncClient.generate = self._patched_async_client_generate

            self._patched = True
            logger.info("Successfully patched Ollama client methods")

        except Exception as e:
            logger.error(f"Failed to patch Ollama client: {e}")

    def _patched_chat(
        self, model: str, messages: List[Dict[str, Any]], **kwargs: Any
    ) -> Any:
        """Patched version of ollama.chat that injects guidelines."""
        try:
            # Get guidelines from guardrails engine
            guidelines = self._get_guidelines_for_messages(messages)

            if guidelines:
                # Inject guidelines into the messages
                modified_messages = self._inject_guidelines_into_messages(
                    messages, guidelines
                )
                logger.debug(
                    f"Injected guidelines into Ollama chat: {len(guidelines)} guidelines"
                )
                if self.original_chat is not None:
                    return self.original_chat(model, modified_messages, **kwargs)
                return None
            else:
                if self.original_chat is not None:
                    return self.original_chat(model, messages, **kwargs)
                return None

        except Exception as e:
            logger.error(f"Error in patched Ollama chat: {e}")
            # Fallback to original method
            if self.original_chat is not None:
                return self.original_chat(model, messages, **kwargs)
            return None

    def _patched_generate(self, model: str, prompt: str, **kwargs: Any) -> Any:
        """Patched version of ollama.generate that injects guidelines."""
        try:
            # Get guidelines from guardrails engine
            guidelines = self._get_guidelines_for_prompt(prompt)

            if guidelines:
                # Inject guidelines into the prompt
                modified_prompt = self._inject_guidelines_into_prompt(
                    prompt, guidelines
                )
                logger.debug(
                    f"Injected guidelines into Ollama generate: {len(guidelines)} guidelines"
                )
                if self.original_generate is not None:
                    return self.original_generate(model, modified_prompt, **kwargs)
                return None
            else:
                if self.original_generate is not None:
                    return self.original_generate(model, prompt, **kwargs)
                return None

        except Exception as e:
            logger.error(f"Error in patched Ollama generate: {e}")
            # Fallback to original method
            if self.original_generate is not None:
                return self.original_generate(model, prompt, **kwargs)
            return None

    def _patched_client_chat(
        self,
        client_instance: Any,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> Any:
        """Patched version of Client.chat that injects guidelines."""
        try:
            # Get guidelines from guardrails engine
            guidelines = self._get_guidelines_for_messages(messages)

            if guidelines:
                # Inject guidelines into the messages
                modified_messages = self._inject_guidelines_into_messages(
                    messages, guidelines
                )
                logger.debug(
                    f"Injected guidelines into Ollama Client.chat: {len(guidelines)} guidelines"
                )
                return client_instance._original_chat(
                    model, modified_messages, **kwargs
                )
            else:
                return client_instance._original_chat(model, messages, **kwargs)

        except Exception as e:
            logger.error(f"Error in patched Ollama Client.chat: {e}")
            # Fallback to original method
            return client_instance._original_chat(model, messages, **kwargs)

    def _patched_client_generate(
        self, client_instance: Any, model: str, prompt: str, **kwargs: Any
    ) -> Any:
        """Patched version of Client.generate that injects guidelines."""
        try:
            # Get guidelines from guardrails engine
            guidelines = self._get_guidelines_for_prompt(prompt)

            if guidelines:
                # Inject guidelines into the prompt
                modified_prompt = self._inject_guidelines_into_prompt(
                    prompt, guidelines
                )
                logger.debug(
                    f"Injected guidelines into Ollama Client.generate: {len(guidelines)} guidelines"
                )
                return client_instance._original_generate(
                    model, modified_prompt, **kwargs
                )
            else:
                return client_instance._original_generate(model, prompt, **kwargs)

        except Exception as e:
            logger.error(f"Error in patched Ollama Client.generate: {e}")
            # Fallback to original method
            return client_instance._original_generate(model, prompt, **kwargs)

    async def _patched_async_client_chat(
        self,
        client_instance: Any,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> Any:
        """Patched version of AsyncClient.chat that injects guidelines."""
        try:
            # Get guidelines from guardrails engine
            guidelines = self._get_guidelines_for_messages(messages)

            if guidelines:
                # Inject guidelines into the messages
                modified_messages = self._inject_guidelines_into_messages(
                    messages, guidelines
                )
                logger.debug(
                    f"Injected guidelines into Ollama AsyncClient.chat: {len(guidelines)} guidelines"
                )
                return await client_instance._original_chat(
                    model, modified_messages, **kwargs
                )
            else:
                return await client_instance._original_chat(model, messages, **kwargs)

        except Exception as e:
            logger.error(f"Error in patched Ollama AsyncClient.chat: {e}")
            # Fallback to original method
            return await client_instance._original_chat(model, messages, **kwargs)

    async def _patched_async_client_generate(
        self, client_instance: Any, model: str, prompt: str, **kwargs: Any
    ) -> Any:
        """Patched version of AsyncClient.generate that injects guidelines."""
        try:
            # Get guidelines from guardrails engine
            guidelines = self._get_guidelines_for_prompt(prompt)

            if guidelines:
                # Inject guidelines into the prompt
                modified_prompt = self._inject_guidelines_into_prompt(
                    prompt, guidelines
                )
                logger.debug(
                    f"Injected guidelines into Ollama AsyncClient.generate: {len(guidelines)} guidelines"
                )
                return await client_instance._original_generate(
                    model, modified_prompt, **kwargs
                )
            else:
                return await client_instance._original_generate(model, prompt, **kwargs)

        except Exception as e:
            logger.error(f"Error in patched Ollama AsyncClient.generate: {e}")
            # Fallback to original method
            return await client_instance._original_generate(model, prompt, **kwargs)

    def _get_guidelines_for_messages(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract user message and get guidelines from guardrails engine."""
        try:
            from rizk.sdk.guardrails.engine import GuardrailsEngine

            # Extract user message from messages
            user_message = self._extract_user_message_from_messages(messages)
            if not user_message:
                return []

            # Get guardrails engine instance
            guardrails_engine = GuardrailsEngine.get_instance()
            if not guardrails_engine or not guardrails_engine.policy_augmentation:
                return []

            # Get guidelines from policy augmentation
            matched_policies = guardrails_engine.policy_augmentation._match_policies(
                user_message
            )
            guidelines = guardrails_engine.policy_augmentation._extract_guidelines(
                matched_policies
            )

            return guidelines

        except Exception as e:
            logger.error(f"Error getting guidelines for Ollama messages: {e}")
            return []

    def _get_guidelines_for_prompt(self, prompt: str) -> List[str]:
        """Get guidelines from guardrails engine for a prompt."""
        try:
            from rizk.sdk.guardrails.engine import GuardrailsEngine

            if not prompt:
                return []

            # Get guardrails engine instance
            guardrails_engine = GuardrailsEngine.get_instance()
            if not guardrails_engine or not guardrails_engine.policy_augmentation:
                return []

            # Get guidelines from policy augmentation
            matched_policies = guardrails_engine.policy_augmentation._match_policies(
                prompt
            )
            guidelines = guardrails_engine.policy_augmentation._extract_guidelines(
                matched_policies
            )

            return guidelines

        except Exception as e:
            logger.error(f"Error getting guidelines for Ollama prompt: {e}")
            return []

    def _extract_user_message_from_messages(
        self, messages: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Extract user message text from Ollama messages."""
        try:
            # Find the last user message
            for message in reversed(messages):
                if isinstance(message, dict) and message.get("role") == "user":
                    content = message.get("content", "")
                    if isinstance(content, str):
                        return content
                    elif isinstance(content, list):
                        # Handle list of content parts
                        text_parts = []
                        for part in content:
                            if isinstance(part, str):
                                text_parts.append(part)
                            elif isinstance(part, dict) and "text" in part:
                                text_parts.append(part["text"])
                        return " ".join(text_parts) if text_parts else None

            return None

        except Exception as e:
            logger.error(f"Error extracting user message from Ollama messages: {e}")
            return None

    def _inject_guidelines_into_messages(
        self, messages: List[Dict[str, Any]], guidelines: List[str]
    ) -> List[Dict[str, Any]]:
        """Inject guidelines into Ollama messages."""
        try:
            if not guidelines:
                return messages

            # Create guidelines text
            guidelines_text = "\n".join([f"- {guideline}" for guideline in guidelines])
            guideline_prompt = (
                f"\n\nPlease follow these guidelines:\n{guidelines_text}\n"
            )

            # Create a copy of messages to avoid modifying the original
            modified_messages = []
            for message in messages:
                modified_messages.append(message.copy())

            # Find the last user message and append guidelines
            for i in range(len(modified_messages) - 1, -1, -1):
                message = modified_messages[i]
                if isinstance(message, dict) and message.get("role") == "user":
                    content = message.get("content", "")
                    if isinstance(content, str):
                        message["content"] = content + guideline_prompt
                        break
                    elif isinstance(content, list):
                        # Handle list of content parts
                        modified_content = content.copy()
                        # Append to the last text part or add new text part
                        for j in range(len(modified_content) - 1, -1, -1):
                            part = modified_content[j]
                            if isinstance(part, str):
                                modified_content[j] = part + guideline_prompt
                                break
                            elif isinstance(part, dict) and "text" in part:
                                part["text"] += guideline_prompt
                                break
                        else:
                            # No text part found, add new text part
                            modified_content.append(
                                {"type": "text", "text": guideline_prompt}
                            )
                        message["content"] = modified_content
                        break

            return modified_messages

        except Exception as e:
            logger.error(f"Error injecting guidelines into Ollama messages: {e}")
            return messages

    def _inject_guidelines_into_prompt(self, prompt: str, guidelines: List[str]) -> str:
        """Inject guidelines into Ollama prompt."""
        try:
            if not guidelines:
                return prompt

            # Create guidelines text
            guidelines_text = "\n".join([f"- {guideline}" for guideline in guidelines])
            guideline_prompt = (
                f"\n\nPlease follow these guidelines:\n{guidelines_text}\n"
            )

            return prompt + guideline_prompt

        except Exception as e:
            logger.error(f"Error injecting guidelines into Ollama prompt: {e}")
            return prompt

    @handle_errors(fail_closed=False, default_return_on_error=False)
    def unpatch_llm_client(self) -> bool:
        """Restore original Ollama client methods."""
        if not OLLAMA_AVAILABLE or not self._patched:
            return False

        try:
            # Restore global functions
            if self.original_chat:
                ollama.chat = self.original_chat

            if self.original_generate:
                ollama.generate = self.original_generate

            # Restore Client methods
            if hasattr(Client, "_original_chat"):
                Client.chat = Client._original_chat
                delattr(Client, "_original_chat")

            if hasattr(Client, "_original_generate"):
                Client.generate = Client._original_generate
                delattr(Client, "_original_generate")

            # Restore AsyncClient methods
            if hasattr(AsyncClient, "_original_chat"):
                AsyncClient.chat = AsyncClient._original_chat
                delattr(AsyncClient, "_original_chat")

            if hasattr(AsyncClient, "_original_generate"):
                AsyncClient.generate = AsyncClient._original_generate
                delattr(AsyncClient, "_original_generate")

            self._patched = False
            logger.info("Successfully unpatched Ollama client methods")
            return True

        except Exception as e:
            logger.error(f"Failed to unpatch Ollama client: {e}")
            return False

    def get_client_info(self) -> Dict[str, Any]:
        """Get information about the Ollama client."""
        if not OLLAMA_AVAILABLE:
            return {"available": False, "reason": "ollama not installed"}

        try:
            import ollama

            return {
                "available": True,
                "library": "ollama",
                "version": getattr(ollama, "__version__", "unknown"),
                "patched": self._patched,
            }
        except Exception as e:
            return {"available": False, "reason": str(e)}
