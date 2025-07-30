"""Adapter for patching the OpenAI Chat Completion API."""

import functools
import logging
from typing import Any, Dict

from rizk.sdk.adapters.llm_base_adapter import BaseLLMAdapter

# Try to import OpenAI client for patching
try:
    import openai

    OPENAI_CLIENT_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_CLIENT_AVAILABLE = False

# Try to import OTel context
try:
    from opentelemetry import context as otel_context
except ImportError:
    otel_context = None  # type: ignore[assignment]

logger = logging.getLogger("rizk.adapters.openai_completion")


class OpenAICompletionAdapter(BaseLLMAdapter):
    """Patches OpenAI Chat Completion API calls for guideline injection."""

    is_available = OPENAI_CLIENT_AVAILABLE

    def patch(self) -> None:
        """Patch the OpenAI chat.completions.create method."""
        logger.debug(
            "OpenAICompletionAdapter: Attempting to patch openai.chat.completions methods..."
        )

        # Get the original method directly from openai
        original_create = openai.chat.completions.create

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
                    # Find the first system message
                    system_msg = next(
                        (m for m in messages if m.get("role") == "system"), None
                    )
                    if system_msg and isinstance(system_msg.get("content"), str):
                        from rizk.sdk.guardrails.engine import GuardrailsEngine

                        guidelines = GuardrailsEngine.get_current_guidelines()

                        if guidelines:
                            # Build augmentation text
                            augmentation_text = "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                            augmentation_text += "\n".join(
                                [f"• {g}" for g in guidelines]
                            )

                            # Inject into system prompt
                            system_msg["content"] += augmentation_text

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

        # Apply patch directly to openai
        openai.chat.completions.create = patched_create
        logger.info(
            "Successfully patched openai.chat.completions.create for augmentation."
        )

        # Also patch the async variant if available
        try:
            # Check if acreate exists before attempting to patch it
            if hasattr(openai.chat.completions, "acreate"):
                original_acreate = openai.chat.completions.acreate

                async def patched_acreate(*args: Any, **kwargs: Any) -> Any:
                    # Similar augmentation logic as above
                    try:
                        messages = kwargs.get("messages") or (
                            args[0].get("messages")
                            if args and isinstance(args[0], dict)
                            else []
                        )
                        if messages:
                            system_msg = next(
                                (m for m in messages if m.get("role") == "system"), None
                            )
                            if system_msg and isinstance(
                                system_msg.get("content"), str
                            ):
                                from rizk.sdk.guardrails.engine import GuardrailsEngine

                                guidelines = GuardrailsEngine.get_current_guidelines()
                                if guidelines:
                                    augmentation_text = (
                                        "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                                    )
                                    augmentation_text += "\n".join(
                                        [f"• {g}" for g in guidelines]
                                    )
                                    system_msg["content"] += augmentation_text
                                    GuardrailsEngine.clear_current_guidelines()
                                    logger.info(
                                        f"Injected {len(guidelines)} policy guidelines into async system prompt"
                                    )
                    except Exception as e:
                        logger.error(
                            f"Policy injection error in async completion: {str(e)}"
                        )

                    return await original_acreate(*args, **kwargs)

                openai.chat.completions.acreate = patched_acreate
                logger.info(
                    "Successfully patched async openai.chat.completions.acreate for augmentation."
                )
            else:
                logger.debug(
                    "OpenAI async completions (acreate) not found, skipping patch."
                )
        except Exception as e:
            logger.debug(f"Failed to patch async completions: {e}")

    def _patch_sync_create(self) -> None:
        """Patches the synchronous openai.chat.completions.create method."""
        try:
            target_obj = openai.chat.completions
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
                    f"Successfully patched openai.chat.completions.{method_name} for augmentation."
                )
            elif hasattr(getattr(target_obj, method_name, None), "_rizk_augmented"):
                logger.debug(f"openai.chat.completions.{method_name} already patched.")
            else:
                logger.warning(
                    f"Could not find openai.chat.completions.{method_name} to patch."
                )
        except AttributeError as e:
            logger.error(f"AttributeError during sync OpenAI patching: {e}")
        except Exception as e:
            logger.error(f"Error patching sync OpenAI client: {e}", exc_info=True)

    def _patch_async_create(self) -> None:
        """Patches the asynchronous chat completions create method."""
        try:
            # Common locations for the async client/methods
            async_locations = [
                getattr(
                    getattr(openai.chat, "completions", None), "async_", None
                ),  # Older pattern?
                getattr(
                    openai.chat.completions, "AsyncCompletions", None
                ),  # Newer pattern?
                # Add other potential locations if library structure changes
            ]

            async_target_obj = None
            for loc in async_locations:
                if loc is not None:
                    async_target_obj = loc
                    break

            if not async_target_obj:
                logger.debug(
                    "OpenAI async completions module/class not found, skipping patch."
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
                    f"Successfully patched async openai.chat.completions method '{async_method_name}'."
                )
            elif hasattr(target_method, "_rizk_augmented"):
                logger.debug(
                    f"Async openai.chat.completions method '{async_method_name}' already patched."
                )

        except AttributeError as e:
            logger.error(f"AttributeError during async OpenAI patching: {e}")
        except Exception as e:
            logger.error(f"Error patching async OpenAI client: {e}", exc_info=True)

    def _inject_guidelines_into_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Injects guidelines into the payload, by appending to the system prompt or creating
        a new system message if none exists.
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
                        f"[OpenAICompletionAdapter] Retrieved {len(guidelines)} guidelines from GuardrailsEngine."
                    )
                    logger.debug(
                        f"Found {len(guidelines)} guidelines to inject at OpenAI Chat Completions call time"
                    )

            # If we couldn't get guidelines from GuardrailsEngine, try legacy OTel method
            if not guidelines and otel_context:
                current_ctx = otel_context.get_current()
                guidelines = otel_context.get_value(
                    "rizk.augmentation.guidelines", context=current_ctx
                )  # type: ignore[assignment]
                if guidelines:
                    logger.debug(
                        f"[OpenAICompletionAdapter] Retrieved {len(guidelines)} guidelines from OTel context (fallback)."
                    )
        except Exception as e:
            logger.debug(f"Error retrieving guidelines from GuardrailsEngine: {e}")
            # Try legacy method if GuardrailsEngine failed
            if otel_context:
                try:
                    current_ctx = otel_context.get_current()
                    guidelines = otel_context.get_value(
                        "rizk.augmentation.guidelines", context=current_ctx
                    )  # type: ignore[assignment]
                except Exception as e2:
                    logger.debug(
                        f"Could not retrieve guidelines from OTel context either: {e2}"
                    )

        if not guidelines:
            logger.debug("No guidelines found to inject in OpenAICompletionAdapter.")
            return kwargs

        modified_kwargs = kwargs.copy()  # Work on a copy
        guidelines_injected = False

        # Only proceed if the 'messages' key is present and it's a list
        if "messages" in modified_kwargs and isinstance(
            modified_kwargs["messages"], list
        ):
            messages = list(modified_kwargs["messages"])
            policy_section_header = "\n\nIMPORTANT POLICY GUIDELINES:"
            formatted_guidelines = (
                policy_section_header + "\n" + "\n".join([f"- {g}" for g in guidelines])
            )
            system_message_found = False

            for i, msg in enumerate(messages):
                if isinstance(msg, dict) and msg.get("role") == "system":
                    system_message_found = True
                    mod_msg = msg.copy()
                    original_content = mod_msg.get("content", "")
                    if not isinstance(original_content, str):
                        original_content = str(original_content)
                        # Avoid duplicate injection by splitting at policy section if it exists
                    if policy_section_header in original_content:
                        original_content = original_content.split(
                            policy_section_header
                        )[0].rstrip()
                    separator = "\n\n" if original_content else ""
                    mod_msg["content"] = (
                        original_content + separator + formatted_guidelines
                    )
                    messages[i] = mod_msg
                    logger.debug(
                        f"Injected {len(guidelines)} guidelines into existing system prompt."
                    )
                    logger.debug(
                        f"Injected {len(guidelines)} policy guidelines into system message at Chat Completions call"
                    )
                    guidelines_injected = True
                    break

            if not system_message_found:
                # No system message found, create and prepend one
                messages.insert(
                    0, {"role": "system", "content": formatted_guidelines.strip()}
                )
                logger.debug(
                    f"No system prompt found. Created and prepended one with {len(guidelines)} guidelines."
                )
                logger.debug(
                    f"Created new system message with {len(guidelines)} policy guidelines at Chat Completions call"
                )
                guidelines_injected = True

            if guidelines_injected:
                modified_kwargs["messages"] = (
                    messages  # Update kwargs with modified messages
                )
        else:
            logger.warning(
                "Could not inject guidelines: 'messages' key not found in kwargs or not a list."
            )

        # Clear context only if injection was attempted (successful or not in finding a usable target)
        if guidelines_injected:
            try:
                # Try to clear via GuardrailsEngine first (preferred)
                from rizk.sdk.guardrails.engine import GuardrailsEngine

                engine = GuardrailsEngine.get_instance()
                if engine:
                    engine.clear_current_guidelines()
                    logger.debug(
                        "Cleared guidelines from GuardrailsEngine after Completion injection."
                    )
                # Fallback to OTel if needed
                elif otel_context:
                    current_ctx = otel_context.get_current()
                    new_ctx = otel_context.set_value(
                        "rizk.augmentation.guidelines", None, current_ctx
                    )
                    otel_context.attach(new_ctx)
                    logger.debug(
                        "Cleared guidelines from OTel context after Completion injection."
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to clear guidelines from context (Completion): {e}"
                )

        return (
            modified_kwargs if guidelines_injected else kwargs
        )  # Return modified only if something was changed
