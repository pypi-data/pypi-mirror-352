"""Rizk Guardrail component for policy-based prompt augmentation and response generation.

Matches input text against defined policies, extracts relevant guidelines,
and uses these to augment prompts or generate policy-aware responses via an LLM.
"""
# mypy: disable-error-code=unreachable

import os
import re
import json
import logging
import inspect
from typing import Dict, Any, List, Optional, Union, TypedDict, Pattern, Callable, Tuple

# Handle yaml import with proper error handling
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None  # type: ignore[assignment]

# Import shared types/protocols
from .fast_rules import PolicyRule  # Reuse PolicyRule definition
from .llm_service import (
    LLMServiceProtocol,
    LLMEvaluationResult,
    DefaultLLMService,
)  # Use the defined protocol
from rizk.sdk.utils.span_utils import safe_set_span_attribute
from opentelemetry import trace

logger = logging.getLogger("rizk.guardrails.augmentation")


# Define expected result structure for augmentation processing
class AugmentationResult(TypedDict, total=False):
    matched_policies: List[PolicyRule]
    extracted_guidelines: List[str]
    augmented_prompt: Optional[str]
    generated_response: Optional[str]  # If LLM generated a direct response
    llm_evaluation: Optional[
        LLMEvaluationResult
    ]  # If LLM was used for evaluation/generation


class PolicyAugmentation:
    """Matches messages to policies and augments prompts or generates responses.

    Loads policies (YAML/JSON), matches them against input messages,
    extracts guidelines, and optionally uses an LLM service to augment
    prompts or generate policy-aware responses.

    Attributes:
        policies_path: Path to the policy definition files.
        llm_service: An instance conforming to LLMServiceProtocol.
        policies: List of loaded and processed policy rules.
    """

    policies_path: str
    llm_service: LLMServiceProtocol
    policies: List[PolicyRule]

    def __init__(
        self, policies_path: str, llm_service: Optional[LLMServiceProtocol] = None
    ):
        """Initializes the PolicyAugmentation component.

        Args:
            policies_path: Path to the directory or file containing policy definitions.
            llm_service: An optional LLM service instance (LLMServiceProtocol).
                         If None, uses DefaultLLMService (passthrough).

        Raises:
            FileNotFoundError: If the policies_path does not exist.
        """
        self.policies_path = policies_path
        if llm_service is None:
            logger.warning(
                "No LLM service provided to PolicyAugmentation, using DefaultLLMService."
            )
            self.llm_service = DefaultLLMService()
        else:
            self.llm_service = llm_service
        self.policies = []
        logger.info(
            f"Initializing PolicyAugmentation with policies path: {self.policies_path}"
        )

        if not os.path.exists(self.policies_path):
            logger.error(f"Policies path does not exist: {self.policies_path}")
            raise FileNotFoundError(f"Policies path not found: {self.policies_path}")

        # TODO: Refactor policy loading into a shared utility with FastRulesEngine
        self._load_and_process_policies()

    # --- Policy Loading & Processing (Duplicated from FastRulesEngine - Needs Refactor) ---
    # NOTE: This section duplicates logic from FastRulesEngine and should ideally
    # be extracted into a shared utility or base class.
    # Keeping it here temporarily for the refactoring step.

    def _compile_patterns(
        self, patterns: List[str], policy_id: str
    ) -> List[Pattern[str]]:
        """Compiles raw regex strings into Pattern objects."""
        # (Identical to FastRulesEngine._compile_patterns)
        compiled = []
        for pattern_str in patterns:
            if not isinstance(pattern_str, str):
                logger.warning(
                    f"[Augmentation] Invalid pattern type ({type(pattern_str)}) in policy {policy_id}. Skipping."
                )
                continue
            try:
                compiled.append(re.compile(pattern_str, re.IGNORECASE))
            except re.error as e:
                logger.error(
                    f"[Augmentation] Invalid regex pattern '{pattern_str}' in policy {policy_id}: {e}. Skipping."
                )
            except Exception as e:
                logger.error(
                    f"[Augmentation] Error compiling pattern '{pattern_str}' in policy {policy_id}: {e}",
                    exc_info=True,
                )
        return compiled

    def _compile_domains(
        self, domains: List[str], policy_id: str
    ) -> List[Pattern[str]]:
        """Compiles domain strings into word-boundary regex Pattern objects."""
        # (Identical to FastRulesEngine._compile_domains)
        compiled = []
        for domain_str in domains:
            if not isinstance(domain_str, str):
                logger.warning(
                    f"[Augmentation] Invalid domain type ({type(domain_str)}) in policy {policy_id}. Skipping."
                )
                continue
            try:
                domain_pattern = r"\b" + re.escape(domain_str) + r"\b"
                compiled.append(re.compile(domain_pattern, re.IGNORECASE))
            except re.error as e:
                logger.error(
                    f"[Augmentation] Error creating regex for domain '{domain_str}' in policy {policy_id}: {e}. Skipping."
                )
            except Exception as e:
                logger.error(
                    f"[Augmentation] Error compiling domain '{domain_str}' in policy {policy_id}: {e}",
                    exc_info=True,
                )
        return compiled

    def _validate_and_process_policy(
        self, policy_data: Dict[str, Any], file_basename: str
    ) -> Optional[PolicyRule]:
        """Validates raw policy data and processes it into PolicyRule format."""
        # (Near-identical to FastRulesEngine._validate_and_process_policy, added logging prefix)
        if not isinstance(policy_data, dict):
            logger.warning(
                f"[Augmentation] Policy item in {file_basename} is not a dictionary. Skipping."
            )
            return None
        policy_id = policy_data.get("id")
        if not policy_id or not isinstance(policy_id, str):
            logger.warning(
                f"[Augmentation] Policy in {file_basename} missing valid string 'id'. Skipping: {policy_data}"
            )
            return None

        processed_policy: PolicyRule = {
            "id": policy_id,
            "description": policy_data.get("description"),
            "action": policy_data.get("action", "allow").lower(),
            # Augmentation doesn't use confidence scores directly like FastRules
        }
        # Extract guidelines specifically
        guidelines = policy_data.get("guidelines")
        if guidelines and isinstance(guidelines, list):
            processed_policy["guidelines"] = [
                str(g) for g in guidelines if isinstance(g, (str, int, float))
            ]
        elif guidelines:
            logger.warning(
                f"[Augmentation] Policy '{policy_id}' has non-list 'guidelines'. Ignoring guidelines."
            )

        # Compile patterns/domains needed for matching
        raw_patterns = policy_data.get("patterns", [])
        if isinstance(raw_patterns, list):
            processed_policy["compiled_patterns"] = self._compile_patterns(
                raw_patterns, policy_id
            )
        elif raw_patterns:
            logger.warning(
                f"[Augmentation] 'patterns' field in policy {policy_id} is not a list. Ignoring."
            )
        raw_domains = policy_data.get("domains", [])
        if isinstance(raw_domains, list):
            processed_policy["compiled_domains"] = self._compile_domains(
                raw_domains, policy_id
            )
        elif raw_domains:
            logger.warning(
                f"[Augmentation] 'domains' field in policy {policy_id} is not a list. Ignoring."
            )

        # A policy might only have guidelines and no patterns/domains if used differently
        if (
            not processed_policy.get("guidelines")
            and not processed_policy.get("compiled_patterns")
            and not processed_policy.get("compiled_domains")
        ):
            logger.debug(
                f"[Augmentation] Policy {policy_id} has no guidelines, patterns, or domains."
            )

        return processed_policy

    def _load_and_process_policies(self) -> None:
        """Loads policies from files and processes them."""
        files_processed = 0
        policies_added = 0

        if os.path.isfile(self.policies_path):
            files_to_process = [self.policies_path]
        elif os.path.isdir(self.policies_path):
            files_to_process = [
                os.path.join(self.policies_path, f)
                for f in os.listdir(self.policies_path)
                if os.path.isfile(os.path.join(self.policies_path, f))
                and f.lower().endswith((".json", ".yaml", ".yml"))
            ]
        else:
            logger.error(
                f"[Augmentation] Policies path is neither file nor directory: {self.policies_path}"
            )
            return

        if not files_to_process:
            logger.warning(
                f"[Augmentation] No policy files found in path: {self.policies_path}"
            )
            return

        for file_path in files_to_process:
            files_processed += 1
            file_basename = os.path.basename(file_path)
            raw_data: Optional[Union[Dict[str, Any], List[Any]]] = None
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    if file_path.lower().endswith(".json"):
                        raw_data = json.load(f)
                    elif file_path.lower().endswith((".yaml", ".yml")):
                        if not YAML_AVAILABLE or yaml is None:
                            logger.warning(
                                f"[Augmentation] Cannot load YAML '{file_basename}': PyYAML missing. Skipping."
                            )
                            continue
                        raw_data = yaml.safe_load(f)
                    else:
                        continue

                policy_list_raw: List[Dict[str, Any]] = []
                if isinstance(raw_data, list):
                    policy_list_raw = raw_data
                elif isinstance(raw_data, dict) and isinstance(
                    raw_data.get("policies"), list
                ):
                    policy_list_raw = raw_data["policies"]
                elif isinstance(raw_data, dict):
                    policy_list_raw = [raw_data]
                else:
                    logger.warning(
                        f"[Augmentation] Unexpected data structure in {file_basename}. Skipping."
                    )
                    continue

                for policy_item in policy_list_raw:
                    processed = self._validate_and_process_policy(
                        policy_item, file_basename
                    )
                    if processed:
                        self.policies.append(processed)
                        policies_added += 1

            except json.JSONDecodeError as e:
                logger.error(
                    f"[Augmentation] Error decoding JSON from {file_basename}: {e}"
                )
            except Exception as e:
                # Combined yaml.YAMLError and other exceptions
                if (
                    YAML_AVAILABLE
                    and yaml is not None
                    and hasattr(yaml, "YAMLError")
                    and isinstance(e, yaml.YAMLError)
                ):
                    logger.error(
                        f"[Augmentation] Error parsing YAML from {file_basename}: {e}"
                    )
                else:
                    logger.error(
                        f"[Augmentation] Unexpected error loading policy from {file_basename}: {e}",
                        exc_info=True,
                    )

        logger.info(
            f"[Augmentation] Processed {files_processed} files. Loaded {policies_added} policies."
        )

    def _match_policies(self, message: str) -> List[PolicyRule]:
        """Matches loaded policies to a message based on patterns/domains.

        Args:
            message: The input text message string.

        Returns:
            A list of matched policy rule dictionaries.
        """
        matched_policies: List[PolicyRule] = []
        matched_ids: set[str] = set()

        if not message or not isinstance(message, str):
            return []
        if not self.policies:
            return []

        for policy in self.policies:
            policy_matched = False
            # Check compiled patterns first
            compiled_patterns = policy.get("compiled_patterns")
            if compiled_patterns:
                for pattern in compiled_patterns:
                    if pattern.search(message):
                        if policy["id"] not in matched_ids:
                            matched_policies.append(policy)
                            matched_ids.add(policy["id"])
                        policy_matched = True
                        break
            if policy_matched:
                continue

            # Check compiled domains if no pattern matched for this policy yet
            compiled_domains = policy.get("compiled_domains")
            if compiled_domains:
                for domain_pattern in compiled_domains:
                    if domain_pattern.search(message):
                        original_domain = domain_pattern.pattern.strip(
                            r"\b"
                        )  # Get original string
                        logger.debug(
                            f"Policy '{policy['id']}' matched by domain '{original_domain}'"
                        )
                        matched_policies.append(policy)
                        matched_ids.add(policy["id"])
                        break

        logger.debug(
            f"_match_policies found {len(matched_policies)} matching policies."
        )
        return matched_policies

    def _extract_guidelines(self, policies: List[PolicyRule]) -> List[str]:
        """Extracts guideline strings from a list of matched policies.

        Args:
            policies: A list of policy rule dictionaries.

        Returns:
            A flat list of unique guideline strings.
        """
        guidelines: List[str] = []
        seen_guidelines: set[str] = set()
        policy_ids_with_guidelines: List[str] = []

        for policy in policies:
            policy_id = policy.get("id", "<unknown>")
            policy_guidelines = policy.get("guidelines", [])
            if policy_guidelines:
                found_guidelines = False
                for guideline in policy_guidelines:
                    if isinstance(guideline, str) and guideline not in seen_guidelines:
                        guidelines.append(guideline)
                        seen_guidelines.add(guideline)
                        found_guidelines = True
                if found_guidelines:
                    policy_ids_with_guidelines.append(policy_id)

        if policy_ids_with_guidelines:
            logger.debug(
                f"Extracted guidelines from policies: {policy_ids_with_guidelines}"
            )
        return guidelines

    async def augment_prompt(
        self, messages: List[Dict[str, str]], context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """
        Augment an LLM prompt with safety guidelines based on detected policies.

        This method examines the user messages, identifies relevant policies,
        and adds guidelines to the system prompt if present.

        Args:
            messages: List of message dictionaries (e.g. for OpenAI chat models)
            context: Optional context information

        Returns:
            The possibly augmented messages list
        """
        if not messages:
            return messages

        # Only process if we have a system message
        system_idx = next(
            (i for i, m in enumerate(messages) if m.get("role") == "system"), None
        )
        if system_idx is None:
            return messages

        # Extract user messages to analyze
        user_messages = [
            m.get("content", "") for m in messages if m.get("role") == "user"
        ]
        if not user_messages:
            return messages

        # Combine user messages for analysis (up to a reasonable limit)
        combined_message = " ".join(user_messages)
        if len(combined_message) > 4000:
            combined_message = combined_message[:4000]  # Truncate if too long

        # Get matched policies and extract guidelines
        matched_policies = self._match_policies(combined_message)

        if not matched_policies:
            return messages

        # Get system message and extract guidelines from matched policies
        system_message = messages[system_idx]
        system_content = system_message.get("content", "")

        guidelines = self._extract_guidelines(matched_policies)

        if not guidelines:
            return messages

        # Store guidelines in context for potential future use
        if context:
            span = trace.get_current_span()
            if span:
                if "conversation_id" in context:
                    safe_set_span_attribute(
                        span, "conversation_id", context["conversation_id"]
                    )
                safe_set_span_attribute(
                    span,
                    "augmentation.matched_policies",
                    ",".join(p["id"] for p in matched_policies),
                )
                safe_set_span_attribute(
                    span, "augmentation.guidelines_count", len(guidelines)
                )

            # Store in OpenTelemetry context for other components
            try:
                logger.debug(
                    f"Attempting to augment prompt with {len(guidelines)} guidelines."
                )
                from opentelemetry import context as otel_context

                otel_ctx = otel_context.get_current()
                new_ctx = otel_context.set_value(
                    "rizk.augmentation.guidelines", guidelines, otel_ctx
                )
                otel_context.attach(new_ctx)
            except Exception as e:
                logger.warning(
                    f"Failed to store guidelines in OpenTelemetry context: {e}"
                )

        # Format the guidelines and add to system prompt
        if system_content:
            formatted_guidelines = "\n\n" + "IMPORTANT POLICY NOTES:\n"
            formatted_guidelines += "\n".join([f"- {g}" for g in guidelines])

            # Avoid duplicate additions
            if "IMPORTANT POLICY NOTES:" not in system_content:
                new_content = system_content + formatted_guidelines
                messages[system_idx]["content"] = new_content

        return messages

    def augment_openai_agents_prompt(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        """
        Augments OpenAI Agents SDK prompts by analyzing function arguments and adding guidelines.

        This method inspects the function signature and arguments to identify
        messages or prompts that need augmentation with safety guidelines.

        Args:
            func: The function being decorated
            *args: Positional arguments to the function
            **kwargs: Keyword arguments to the function

        Returns:
            Tuple of (modified_args, modified_kwargs)
        """
        tracer = trace.get_tracer("rizk.guardrails.augmentation")
        with tracer.start_as_current_span(
            "rizk.guardrails.augment_openai_agents_prompt"
        ) as span:
            safe_set_span_attribute(span, "function.name", func.__name__)

            try:
                # Get function signature to understand parameters
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                # Look for message parameters in common argument names
                message_param_names = ["messages", "prompt", "input", "text", "content"]
                message_content = None

                for param_name in message_param_names:
                    if param_name in bound_args.arguments:
                        param_value = bound_args.arguments[param_name]
                        if isinstance(param_value, str):
                            message_content = param_value
                            break
                        elif (
                            isinstance(param_value, list)
                            and param_value
                            and isinstance(param_value[0], dict)
                        ):
                            # Extract content from message list
                            user_messages = [
                                m.get("content", "")
                                for m in param_value
                                if m.get("role") == "user"
                            ]
                            if user_messages:
                                message_content = " ".join(user_messages)
                                break

                if not message_content:
                    logger.debug("No message content found for augmentation")
                    return args, kwargs

                # Match policies and extract guidelines
                matched_policies = self._match_policies(message_content)
                if not matched_policies:
                    logger.debug("No policies matched for augmentation")
                    return args, kwargs

                guidelines = self._extract_guidelines(matched_policies)
                if not guidelines:
                    logger.debug("No guidelines extracted from matched policies")
                    return args, kwargs

                # Store guidelines in OpenTelemetry context for runtime injection
                try:
                    from opentelemetry import context as otel_context

                    current_ctx = otel_context.get_current()
                    new_ctx = otel_context.set_value(
                        "rizk.augmentation.guidelines", guidelines, current_ctx
                    )
                    otel_context.attach(new_ctx)
                    logger.info(
                        f"Stored {len(guidelines)} guidelines in OTel context for OpenAI Agents injection"
                    )
                    safe_set_span_attribute(
                        span, "augmentation.guidelines_count", len(guidelines)
                    )
                except Exception as e:
                    logger.warning(f"Failed to store guidelines in OTel context: {e}")

                return args, kwargs

            except Exception as e:
                logger.error(
                    f"Error in augment_openai_agents_prompt: {e}", exc_info=True
                )
                return args, kwargs

    async def process_message(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AugmentationResult:
        """Processes a message: matches policies and extracts guidelines.

        This method primarily focuses on identifying relevant policies and their
        guidelines based on the input message. It does not perform LLM generation
        itself but prepares the necessary information.

        Args:
            message: The input message string.
            context: Optional context dictionary (currently unused in this method).

        Returns:
            An AugmentationResult dictionary containing matched policies and guidelines.
        """
        context = context or {}
        matched = self._match_policies(message)
        guidelines = self._extract_guidelines(matched)

        result = AugmentationResult(
            matched_policies=matched,
            extracted_guidelines=guidelines,
            # augmented_prompt and generated_response are not set here
        )

        logger.info(
            f"Augmentation processed message. Matched {len(matched)} policies, extracted {len(guidelines)} guidelines."
        )
        return result

    # Potential future method for LLM-based augmentation/response:
    # async def generate_policy_aware_response(self, message: str, context: Dict[str, Any]) -> AugmentationResult:
    #     """ Matches policies and uses LLM to generate a response adhering to guidelines. """
    #     matched = self._match_policies(message)
    #     guidelines = self._extract_guidelines(matched)
    #     if not guidelines:
    #         # Handle case with no guidelines - maybe call normal LLM or return default?
    #         pass
    #
    #     # Construct prompt for LLM asking it to respond based on message + guidelines
    #     generation_prompt = ...
    #
    #     if isinstance(self.llm_service, DefaultLLMService):
    #          logger.warning("Cannot generate policy-aware response with DefaultLLMService.")
    #          # Return empty/default response
    #     else:
    #          # Assume llm_service has a suitable generation method
    #          # generated_text = await self.llm_service.generate(generation_prompt, ...)
    #          pass
    #
    #     return AugmentationResult(...)

    def _get_caller_frame_info(self) -> Dict[str, Any]:
        """Get information about the calling frame for context."""
        try:
            # Walk up the call stack to find the first frame outside this module
            frame = inspect.currentframe()
            if frame is not None:
                caller_frame = frame.f_back
                while caller_frame is not None:
                    frame_info = inspect.getframeinfo(caller_frame)
                    if not frame_info.filename.endswith("policy_augmentation.py"):
                        return {
                            "filename": frame_info.filename,
                            "function": frame_info.function,
                            "lineno": frame_info.lineno,
                        }
                    caller_frame = caller_frame.f_back

            return {"filename": "unknown", "function": "unknown", "lineno": 0}
        except Exception:
            return {"filename": "unknown", "function": "unknown", "lineno": 0}
