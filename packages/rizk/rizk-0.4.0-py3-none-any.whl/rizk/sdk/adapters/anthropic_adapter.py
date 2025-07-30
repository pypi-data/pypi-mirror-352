"""Adapter for patching the Anthropic Messages API."""

import functools
import logging
from typing import Any, Dict, Optional

from rizk.sdk.adapters.llm_base_adapter import BaseLLMAdapter

# Try to import Anthropic client for patching
try:
    import anthropic

    ANTHROPIC_CLIENT_AVAILABLE = True
    anthropic_module: Optional[Any] = anthropic
except ImportError:
    anthropic = None  # type: ignore[assignment]
    anthropic_module = None
    ANTHROPIC_CLIENT_AVAILABLE = False

# Try to import OTel context
try:
    from opentelemetry import context as otel_context
except ImportError:
    otel_context = None  # type: ignore[assignment]

logger = logging.getLogger("rizk.adapters.anthropic")


class AnthropicAdapter(BaseLLMAdapter):
    """Patches Anthropic Messages API calls for guideline injection."""

    is_available = ANTHROPIC_CLIENT_AVAILABLE

    def patch(self) -> None:
        """Patch the Anthropic messages.create method."""
        logger.debug(
            "AnthropicAdapter: Attempting to patch anthropic.messages.create methods..."
        )

        if not ANTHROPIC_CLIENT_AVAILABLE or anthropic_module is None:
            logger.warning("Anthropic client not available. Skipping patch.")
            return

        try:
            # Get the original method directly from anthropic
            if hasattr(anthropic_module, "resources") and hasattr(
                anthropic_module.resources, "messages"
            ):
                if hasattr(anthropic_module.resources.messages, "create"):
                    original_create = anthropic_module.resources.messages.create
                else:
                    logger.warning(
                        "Could not find messages.create method in anthropic.resources.messages"
                    )
                    return
            elif hasattr(anthropic_module, "messages") and hasattr(
                anthropic_module.messages, "create"
            ):
                original_create = anthropic_module.messages.create
            else:
                logger.warning(
                    "Could not find messages.create method in anthropic module"
                )
                return

            # Define wrapper function
            def patched_create(*args: Any, **kwargs: Any) -> Any:
                try:
                    # Extract messages from args/kwargs
                    messages = kwargs.get("messages") or (
                        args[0].get("messages")
                        if args and isinstance(args[0], dict)
                        else []
                    )

                    if messages:
                        # Find the last user message to augment
                        user_msg = None
                        for i in range(len(messages) - 1, -1, -1):
                            if messages[i].get("role") == "user":
                                user_msg = messages[i]
                                break

                        if user_msg and isinstance(user_msg.get("content"), str):
                            from rizk.sdk.guardrails.engine import GuardrailsEngine

                            guidelines = GuardrailsEngine.get_current_guidelines()

                            if guidelines:
                                # Build augmentation text
                                augmentation_text = "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                                augmentation_text += "\n".join(
                                    [f"• {g}" for g in guidelines]
                                )

                                # Inject into user message content
                                user_msg["content"] += augmentation_text

                                # Clear context to prevent double-injection
                                GuardrailsEngine.clear_current_guidelines()

                                # Debug logging
                                logger.info(
                                    f"Injected {len(guidelines)} policy guidelines into user message"
                                )

                        # Handle system prompt augmentation if no user message found
                        elif not user_msg:
                            from rizk.sdk.guardrails.engine import GuardrailsEngine

                            guidelines = GuardrailsEngine.get_current_guidelines()

                            if guidelines:
                                # Check if there's a system parameter to augment
                                system_prompt = kwargs.get("system", "")
                                if isinstance(system_prompt, str):
                                    augmentation_text = (
                                        "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                                    )
                                    augmentation_text += "\n".join(
                                        [f"• {g}" for g in guidelines]
                                    )
                                    kwargs["system"] = system_prompt + augmentation_text
                                elif isinstance(system_prompt, list):
                                    # Handle system prompt as list of content blocks
                                    augmentation_text = (
                                        "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                                    )
                                    augmentation_text += "\n".join(
                                        [f"• {g}" for g in guidelines]
                                    )
                                    system_prompt.append(
                                        {"type": "text", "text": augmentation_text}
                                    )
                                    kwargs["system"] = system_prompt

                                # Clear context to prevent double-injection
                                GuardrailsEngine.clear_current_guidelines()

                                # Debug logging
                                logger.info(
                                    f"Injected {len(guidelines)} policy guidelines into system prompt"
                                )

                except Exception as e:
                    logger.error(f"Policy injection error: {str(e)}")

                # Call the original method
                return original_create(*args, **kwargs)

            # Apply patch directly to anthropic - handle different module structures
            if hasattr(anthropic_module, "resources") and hasattr(
                anthropic_module.resources, "messages"
            ):
                anthropic_module.resources.messages.create = patched_create
            elif hasattr(anthropic_module, "messages"):
                anthropic_module.messages.create = patched_create

            logger.info(
                "Successfully patched anthropic.messages.create for augmentation."
            )

            # Also patch the async variant if available
            try:
                # Check if acreate exists before attempting to patch it
                async_target = None
                if hasattr(anthropic_module, "resources") and hasattr(
                    anthropic_module.resources, "messages"
                ):
                    if hasattr(anthropic_module.resources.messages, "acreate"):
                        async_target = anthropic_module.resources.messages
                        original_acreate = anthropic_module.resources.messages.acreate
                elif hasattr(anthropic_module, "messages") and hasattr(
                    anthropic_module.messages, "acreate"
                ):
                    async_target = anthropic_module.messages
                    original_acreate = anthropic_module.messages.acreate

                if async_target is not None:

                    async def patched_acreate(*args: Any, **kwargs: Any) -> Any:
                        # Similar augmentation logic as above
                        try:
                            messages = kwargs.get("messages") or (
                                args[0].get("messages")
                                if args and isinstance(args[0], dict)
                                else []
                            )
                            if messages:
                                # Find the last user message to augment
                                user_msg = None
                                for i in range(len(messages) - 1, -1, -1):
                                    if messages[i].get("role") == "user":
                                        user_msg = messages[i]
                                        break

                                if user_msg and isinstance(
                                    user_msg.get("content"), str
                                ):
                                    from rizk.sdk.guardrails.engine import (
                                        GuardrailsEngine,
                                    )

                                    guidelines = (
                                        GuardrailsEngine.get_current_guidelines()
                                    )
                                    if guidelines:
                                        augmentation_text = (
                                            "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                                        )
                                        augmentation_text += "\n".join(
                                            [f"• {g}" for g in guidelines]
                                        )
                                        user_msg["content"] += augmentation_text
                                        GuardrailsEngine.clear_current_guidelines()
                                        logger.info(
                                            f"Injected {len(guidelines)} policy guidelines into async user message"
                                        )

                                # Handle system prompt augmentation if no user message found
                                elif not user_msg:
                                    from rizk.sdk.guardrails.engine import (
                                        GuardrailsEngine,
                                    )

                                    guidelines = (
                                        GuardrailsEngine.get_current_guidelines()
                                    )

                                    if guidelines:
                                        system_prompt = kwargs.get("system", "")
                                        if isinstance(system_prompt, str):
                                            augmentation_text = (
                                                "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                                            )
                                            augmentation_text += "\n".join(
                                                [f"• {g}" for g in guidelines]
                                            )
                                            kwargs["system"] = (
                                                system_prompt + augmentation_text
                                            )
                                        elif isinstance(system_prompt, list):
                                            augmentation_text = (
                                                "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                                            )
                                            augmentation_text += "\n".join(
                                                [f"• {g}" for g in guidelines]
                                            )
                                            system_prompt.append(
                                                {
                                                    "type": "text",
                                                    "text": augmentation_text,
                                                }
                                            )
                                            kwargs["system"] = system_prompt

                                        GuardrailsEngine.clear_current_guidelines()
                                        logger.info(
                                            f"Injected {len(guidelines)} policy guidelines into async system prompt"
                                        )
                        except Exception as e:
                            logger.error(
                                f"Policy injection error in async messages: {str(e)}"
                            )

                        return await original_acreate(*args, **kwargs)

                    async_target.acreate = patched_acreate
                    logger.info(
                        "Successfully patched async anthropic.messages.acreate for augmentation."
                    )
                else:
                    logger.debug(
                        "Anthropic async messages (acreate) not found, skipping patch."
                    )
            except Exception as e:
                logger.debug(f"Failed to patch async messages: {e}")

        except Exception as e:
            logger.error(f"Error patching Anthropic client: {e}", exc_info=True)

    def _patch_sync_create(self) -> None:
        """Patches the synchronous anthropic.messages.create method."""
        if not ANTHROPIC_CLIENT_AVAILABLE or anthropic_module is None:
            return

        try:
            target_obj = None
            if hasattr(anthropic_module, "resources") and hasattr(
                anthropic_module.resources, "messages"
            ):
                target_obj = anthropic_module.resources.messages
            elif hasattr(anthropic_module, "messages"):
                target_obj = anthropic_module.messages

            if target_obj is None:
                logger.warning("Could not find messages object to patch")
                return

            method_name = "create"
            if hasattr(target_obj, method_name) and not hasattr(
                getattr(target_obj, method_name), "_rizk_augmented"
            ):
                original_create = getattr(target_obj, method_name)

                @functools.wraps(original_create)
                def patched_create(*args: Any, **kwargs: Any) -> Any:
                    modified_kwargs = self._inject_guidelines_into_kwargs(kwargs)
                    return original_create(*args, **modified_kwargs)

                setattr(patched_create, "_rizk_augmented", True)
                setattr(target_obj, method_name, patched_create)
                logger.info(
                    f"Successfully patched anthropic.messages.{method_name} for augmentation."
                )
            elif hasattr(getattr(target_obj, method_name, None), "_rizk_augmented"):
                logger.debug(f"anthropic.messages.{method_name} already patched.")
            else:
                logger.warning(
                    f"Could not find anthropic.messages.{method_name} to patch."
                )
        except AttributeError as e:
            logger.error(f"AttributeError during sync Anthropic patching: {e}")
        except Exception as e:
            logger.error(f"Error patching sync Anthropic client: {e}", exc_info=True)

    def _patch_async_create(self) -> None:
        """Patches the asynchronous messages create method."""
        if not ANTHROPIC_CLIENT_AVAILABLE or anthropic_module is None:
            return

        try:
            # Common locations for the async client/methods
            async_locations = []

            # Try resources.messages structure first
            if hasattr(anthropic_module, "resources") and hasattr(
                anthropic_module.resources, "messages"
            ):
                async_locations.append(anthropic_module.resources.messages)

            # Try direct messages structure
            if hasattr(anthropic_module, "messages"):
                async_locations.extend(
                    [
                        getattr(
                            getattr(anthropic_module.messages, "async_", None),
                            "create",
                            None,
                        ),  # Older pattern?
                        getattr(
                            anthropic_module.messages, "AsyncMessages", None
                        ),  # Newer pattern?
                        anthropic_module.messages,  # Direct access
                    ]
                )

            async_target_obj = None
            for loc in async_locations:
                if loc is not None and hasattr(loc, "acreate"):
                    async_target_obj = loc
                    break

            if not async_target_obj:
                logger.debug(
                    "Anthropic async messages module/class not found, skipping patch."
                )
                return

            # Determine the correct async create method name (e.g., create, acreate)
            async_method_name = None
            for name_to_check in ["create", "acreate"]:  # Check common names
                if hasattr(async_target_obj, name_to_check):
                    async_method_name = name_to_check
                    break

            if not async_method_name:
                logger.debug(
                    f"Could not find async create method on {async_target_obj}, skipping patch."
                )
                return

            target_method = getattr(async_target_obj, async_method_name)
            if not hasattr(target_method, "_rizk_augmented"):
                original_async_create = target_method

                @functools.wraps(original_async_create)
                async def patched_async_create(*args: Any, **kwargs: Any) -> Any:
                    modified_kwargs = self._inject_guidelines_into_kwargs(kwargs)
                    return await original_async_create(*args, **modified_kwargs)

                setattr(patched_async_create, "_rizk_augmented", True)
                setattr(async_target_obj, async_method_name, patched_async_create)
                logger.info(
                    f"Successfully patched async anthropic.messages method '{async_method_name}'."
                )
            elif hasattr(target_method, "_rizk_augmented"):
                logger.debug(
                    f"Async anthropic.messages method '{async_method_name}' already patched."
                )

        except AttributeError as e:
            logger.error(f"AttributeError during async Anthropic patching: {e}")
        except Exception as e:
            logger.error(f"Error patching async Anthropic client: {e}", exc_info=True)

    def _inject_guidelines_into_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Injects guidelines into the payload, by appending to the user message or system prompt.
        """
        guidelines = None

        # First try getting guidelines through GuardrailsEngine (newer, preferred method)
        try:
            from rizk.sdk.guardrails.engine import GuardrailsEngine

            engine = GuardrailsEngine.get_instance()
            if engine:
                guidelines = engine.get_current_guidelines()
                if guidelines:
                    logger.debug(
                        f"[AnthropicAdapter] Retrieved {len(guidelines)} guidelines from GuardrailsEngine."
                    )
                    logger.debug(
                        f"Found {len(guidelines)} guidelines to inject at Anthropic Messages call time"
                    )

            # If we couldn't get guidelines from GuardrailsEngine, try legacy OTel method
            if not guidelines and otel_context is not None:
                try:
                    current_context = otel_context.get_current()
                    otel_guidelines = current_context.get("rizk_guidelines")
                    if otel_guidelines and isinstance(otel_guidelines, list):
                        guidelines = otel_guidelines
                        logger.debug(
                            f"[AnthropicAdapter] Retrieved {len(guidelines)} guidelines from OTel context."
                        )
                except Exception as e:
                    logger.debug(
                        f"[AnthropicAdapter] Could not retrieve guidelines from OTel context: {e}"
                    )

            if not guidelines:
                logger.debug("[AnthropicAdapter] No guidelines found to inject.")
                return kwargs

            # Create a copy of kwargs to avoid modifying the original
            modified_kwargs = kwargs.copy()

            # Inject guidelines into messages
            messages = modified_kwargs.get("messages", [])
            if messages:
                # Find the last user message to augment
                user_msg_index = None
                for i in range(len(messages) - 1, -1, -1):
                    if messages[i].get("role") == "user":
                        user_msg_index = i
                        break

                if user_msg_index is not None:
                    # Create a copy of messages to avoid modifying the original
                    messages_copy = messages.copy()
                    user_msg = messages_copy[user_msg_index].copy()

                    # Augment user message content
                    content = user_msg.get("content", "")
                    if isinstance(content, str):
                        augmentation_text = "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                        augmentation_text += "\n".join([f"• {g}" for g in guidelines])
                        user_msg["content"] = content + augmentation_text
                        messages_copy[user_msg_index] = user_msg
                        modified_kwargs["messages"] = messages_copy

                        logger.info(
                            f"Injected {len(guidelines)} policy guidelines into user message"
                        )
                    elif isinstance(content, list):
                        # Handle content as list of content blocks
                        content_copy = content.copy()
                        augmentation_text = "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                        augmentation_text += "\n".join([f"• {g}" for g in guidelines])
                        content_copy.append({"type": "text", "text": augmentation_text})
                        user_msg["content"] = content_copy
                        messages_copy[user_msg_index] = user_msg
                        modified_kwargs["messages"] = messages_copy

                        logger.info(
                            f"Injected {len(guidelines)} policy guidelines into user message content blocks"
                        )
                else:
                    # No user message found, try to augment system prompt
                    system_prompt = modified_kwargs.get("system", "")
                    if isinstance(system_prompt, str):
                        augmentation_text = "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                        augmentation_text += "\n".join([f"• {g}" for g in guidelines])
                        modified_kwargs["system"] = system_prompt + augmentation_text
                        logger.info(
                            f"Injected {len(guidelines)} policy guidelines into system prompt"
                        )
                    elif isinstance(system_prompt, list):
                        # Handle system prompt as list of content blocks
                        system_copy = system_prompt.copy()
                        augmentation_text = "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                        augmentation_text += "\n".join([f"• {g}" for g in guidelines])
                        system_copy.append({"type": "text", "text": augmentation_text})
                        modified_kwargs["system"] = system_copy
                        logger.info(
                            f"Injected {len(guidelines)} policy guidelines into system prompt blocks"
                        )
            else:
                # No messages, try to augment system prompt
                system_prompt = modified_kwargs.get("system", "")
                if isinstance(system_prompt, str):
                    augmentation_text = "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                    augmentation_text += "\n".join([f"• {g}" for g in guidelines])
                    modified_kwargs["system"] = system_prompt + augmentation_text
                    logger.info(
                        f"Injected {len(guidelines)} policy guidelines into system prompt"
                    )

            # Clear guidelines from context to prevent double-injection
            if engine:
                engine.clear_current_guidelines()

            return modified_kwargs

        except Exception as e:
            logger.error(
                f"Error injecting guidelines into Anthropic request: {e}", exc_info=True
            )
            return kwargs
