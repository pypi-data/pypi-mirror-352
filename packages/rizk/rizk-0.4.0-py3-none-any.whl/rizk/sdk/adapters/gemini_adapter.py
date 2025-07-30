"""
Gemini LLM Adapter for Rizk SDK

This adapter provides integration with Google's Gemini API for LLM guardrails and observability.
It patches the Gemini client to inject guidelines and apply policy enforcement.
"""

import logging
from typing import Any, Dict, List, Optional, Callable

from rizk.sdk.adapters.llm_base_adapter import BaseLLMAdapter
from rizk.sdk.utils.error_handler import handle_errors

logger = logging.getLogger(__name__)

# Check if google-generativeai is available
try:
    import google.generativeai as genai  # noqa: F401
    from google.generativeai.types import GenerateContentResponse  # noqa: F401

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.debug("google-generativeai not available, Gemini adapter will be disabled")


class GeminiAdapter(BaseLLMAdapter):
    """Adapter for Google Gemini API integration with Rizk SDK guardrails."""

    is_available = GEMINI_AVAILABLE

    # Type annotations for original methods
    original_generate_content: Optional[Callable[..., Any]]
    original_generate_content_async: Optional[Callable[..., Any]]
    _patched: bool

    def __init__(self) -> None:
        super().__init__()
        self.original_generate_content = None
        self.original_generate_content_async = None
        self._patched = False

    def patch(self) -> None:
        """Patch Gemini client methods to inject guidelines."""
        if not GEMINI_AVAILABLE:
            logger.debug("Gemini not available, skipping patching")
            return

        if self._patched:
            logger.debug("Gemini client already patched")
            return

        try:
            # Patch the GenerativeModel.generate_content method
            from google.generativeai import GenerativeModel

            if hasattr(GenerativeModel, "generate_content"):
                self.original_generate_content = GenerativeModel.generate_content
                GenerativeModel.generate_content = self._patched_generate_content

            if hasattr(GenerativeModel, "generate_content_async"):
                self.original_generate_content_async = (
                    GenerativeModel.generate_content_async
                )
                GenerativeModel.generate_content_async = (
                    self._patched_generate_content_async
                )

            self._patched = True
            logger.info("Successfully patched Gemini GenerativeModel methods")

        except Exception as e:
            logger.error(f"Failed to patch Gemini client: {e}")

    def _patched_generate_content(
        self, model_instance: Any, contents: Any, **kwargs: Any
    ) -> Any:
        """Patched version of GenerativeModel.generate_content that injects guidelines."""
        try:
            # Get guidelines from guardrails engine
            guidelines = self._get_guidelines_for_content(contents)

            if guidelines:
                # Inject guidelines into the content
                modified_contents = self._inject_guidelines_into_content(
                    contents, guidelines
                )
                logger.debug(
                    f"Injected guidelines into Gemini content: {len(guidelines)} guidelines"
                )
                if self.original_generate_content is not None:
                    return self.original_generate_content(
                        model_instance, modified_contents, **kwargs
                    )
                return None
            else:
                if self.original_generate_content is not None:
                    return self.original_generate_content(
                        model_instance, contents, **kwargs
                    )
                return None

        except Exception as e:
            logger.error(f"Error in patched Gemini generate_content: {e}")
            # Fallback to original method
            if self.original_generate_content is not None:
                return self.original_generate_content(
                    model_instance, contents, **kwargs
                )
            return None

    async def _patched_generate_content_async(
        self, model_instance: Any, contents: Any, **kwargs: Any
    ) -> Any:
        """Patched version of GenerativeModel.generate_content_async that injects guidelines."""
        try:
            # Get guidelines from guardrails engine
            guidelines = self._get_guidelines_for_content(contents)

            if guidelines:
                # Inject guidelines into the content
                modified_contents = self._inject_guidelines_into_content(
                    contents, guidelines
                )
                logger.debug(
                    f"Injected guidelines into Gemini content: {len(guidelines)} guidelines"
                )
                if self.original_generate_content_async is not None:
                    return await self.original_generate_content_async(
                        model_instance, modified_contents, **kwargs
                    )
                return None
            else:
                if self.original_generate_content_async is not None:
                    return await self.original_generate_content_async(
                        model_instance, contents, **kwargs
                    )
                return None

        except Exception as e:
            logger.error(f"Error in patched Gemini generate_content_async: {e}")
            # Fallback to original method
            if self.original_generate_content_async is not None:
                return await self.original_generate_content_async(
                    model_instance, contents, **kwargs
                )
            return None

    def _get_guidelines_for_content(self, contents: Any) -> List[str]:
        """Extract user message and get guidelines from guardrails engine."""
        try:
            from rizk.sdk.guardrails.engine import GuardrailsEngine

            # Extract text content from Gemini contents
            user_message = self._extract_user_message(contents)
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
            logger.error(f"Error getting guidelines for Gemini content: {e}")
            return []

    def _extract_user_message(self, contents: Any) -> Optional[str]:
        """Extract user message text from Gemini contents."""
        try:
            if isinstance(contents, str):
                return contents
            elif isinstance(contents, list):
                # Handle list of content parts
                text_parts = []
                for content in contents:
                    if isinstance(content, str):
                        text_parts.append(content)
                    elif hasattr(content, "text"):
                        text_parts.append(str(content.text))
                    elif isinstance(content, dict) and "text" in content:
                        text_parts.append(str(content["text"]))
                return " ".join(text_parts) if text_parts else None
            elif hasattr(contents, "text"):
                return str(contents.text)
            elif isinstance(contents, dict) and "text" in contents:
                return str(contents["text"])
            else:
                logger.debug(f"Unknown Gemini content format: {type(contents)}")
                return None

        except Exception as e:
            logger.error(f"Error extracting user message from Gemini content: {e}")
            return None

    def _inject_guidelines_into_content(
        self, contents: Any, guidelines: List[str]
    ) -> Any:
        """Inject guidelines into Gemini content."""
        try:
            if not guidelines:
                return contents

            # Create guidelines text
            guidelines_text = "\n".join([f"- {guideline}" for guideline in guidelines])
            guideline_prompt = (
                f"\n\nPlease follow these guidelines:\n{guidelines_text}\n"
            )

            if isinstance(contents, str):
                # Simple string content
                return contents + guideline_prompt
            elif isinstance(contents, list):
                # List of content parts - append to the last text part or add new part
                modified_contents = contents.copy()

                # Find the last text content and append guidelines
                for i in range(len(modified_contents) - 1, -1, -1):
                    content = modified_contents[i]
                    if isinstance(content, str):
                        modified_contents[i] = content + guideline_prompt
                        break
                    elif hasattr(content, "text"):
                        content.text += guideline_prompt
                        break
                    elif isinstance(content, dict) and "text" in content:
                        content["text"] += guideline_prompt
                        break
                else:
                    # No text content found, append as new string
                    modified_contents.append(guideline_prompt)

                return modified_contents
            elif hasattr(contents, "text"):
                # Content object with text attribute
                contents.text += guideline_prompt
                return contents
            elif isinstance(contents, dict) and "text" in contents:
                # Dictionary with text key
                contents["text"] += guideline_prompt
                return contents
            else:
                logger.warning(
                    f"Cannot inject guidelines into unknown Gemini content format: {type(contents)}"
                )
                return contents

        except Exception as e:
            logger.error(f"Error injecting guidelines into Gemini content: {e}")
            return contents

    @handle_errors(fail_closed=False, default_return_on_error=False)
    def unpatch_llm_client(self) -> bool:
        """Restore original Gemini client methods."""
        if not GEMINI_AVAILABLE or not self._patched:
            return False

        try:
            from google.generativeai import GenerativeModel

            if self.original_generate_content:
                GenerativeModel.generate_content = self.original_generate_content

            if self.original_generate_content_async:
                GenerativeModel.generate_content_async = (
                    self.original_generate_content_async
                )

            self._patched = False
            logger.info("Successfully unpatched Gemini GenerativeModel methods")
            return True

        except Exception as e:
            logger.error(f"Failed to unpatch Gemini client: {e}")
            return False

    def get_client_info(self) -> Dict[str, Any]:
        """Get information about the Gemini client."""
        if not GEMINI_AVAILABLE:
            return {"available": False, "reason": "google-generativeai not installed"}

        try:
            import google.generativeai as genai

            return {
                "available": True,
                "library": "google-generativeai",
                "version": getattr(genai, "__version__", "unknown"),
                "patched": self._patched,
            }
        except Exception as e:
            return {"available": False, "reason": str(e)}
