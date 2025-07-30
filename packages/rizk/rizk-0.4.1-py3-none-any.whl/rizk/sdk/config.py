"""Configuration management for the Rizk SDK.

Provides centralized configuration management with validation, environment variable
parsing, and sensible defaults.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

# Configure logger for config utilities
logger = logging.getLogger("rizk.config")


@dataclass
class RizkConfig:
    """Centralized configuration for the Rizk SDK.

    This class provides a single source of truth for all SDK configuration,
    with automatic environment variable parsing, validation, and sensible defaults.
    """

    # Core settings
    app_name: str = "RizkApp"
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("RIZK_API_KEY"))

    # OpenTelemetry settings
    opentelemetry_endpoint: Optional[str] = field(
        default_factory=lambda: os.getenv("RIZK_OPENTELEMETRY_ENDPOINT")
    )
    tracing_enabled: bool = field(
        default_factory=lambda: os.getenv("RIZK_TRACING_ENABLED", "true").lower()
        == "true"
    )
    trace_content: bool = field(
        default_factory=lambda: os.getenv("RIZK_TRACE_CONTENT", "true").lower()
        == "true"
    )
    metrics_enabled: bool = field(
        default_factory=lambda: os.getenv("RIZK_METRICS_ENABLED", "true").lower()
        == "true"
    )

    # Logging settings
    logging_enabled: bool = field(
        default_factory=lambda: os.getenv("RIZK_LOGGING_ENABLED", "false").lower()
        == "true"
    )

    # Guardrails settings
    policies_path: Optional[str] = field(default=None)
    policy_enforcement: bool = field(
        default_factory=lambda: os.getenv("RIZK_POLICY_ENFORCEMENT", "true").lower()
        == "true"
    )

    # Telemetry settings
    telemetry_enabled: bool = field(
        default_factory=lambda: os.getenv("RIZK_TELEMETRY", "false").lower() == "true"
    )

    # Performance settings
    lazy_loading: bool = field(
        default_factory=lambda: os.getenv("RIZK_LAZY_LOADING", "true").lower() == "true"
    )
    framework_detection_cache_size: int = field(
        default_factory=lambda: int(os.getenv("RIZK_FRAMEWORK_CACHE_SIZE", "1000"))
    )

    # Debug settings
    debug_mode: bool = field(
        default_factory=lambda: os.getenv("RIZK_DEBUG", "false").lower() == "true"
    )
    verbose: bool = field(
        default_factory=lambda: os.getenv("RIZK_VERBOSE", "false").lower() == "true"
    )

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        # Resolve policies path if not explicitly set
        if self.policies_path is None:
            self.policies_path = self._resolve_policies_path()

    def _resolve_policies_path(self) -> str:
        """Determines the path to the guardrail policies directory or file.

        Resolution order:
        1. RIZK_POLICIES_PATH environment variable (can be file or directory).
        2. `./guardrails` directory relative to the current working directory.
        3. The bundled `rizk/sdk/guardrails` directory.

        Returns:
            str: The absolute path to the determined policies file or directory.
        """
        # 1. Check environment variable
        env_path_str = os.getenv("RIZK_POLICIES_PATH")
        if env_path_str:
            abs_env_path = os.path.abspath(env_path_str)
            if os.path.exists(abs_env_path):
                logger.debug(
                    f"Using policies path from RIZK_POLICIES_PATH: {abs_env_path}"
                )
                return abs_env_path
            else:
                logger.warning(
                    f"RIZK_POLICIES_PATH ('{env_path_str}') is set but does not exist. "
                    "Falling back to standard locations."
                )

        # 2. Check for local ./guardrails directory
        local_guardrails_path = os.path.abspath(os.path.join(os.getcwd(), "guardrails"))
        if os.path.isdir(local_guardrails_path):
            # Check if it contains any policy files
            policy_files_exist = any(
                f.lower().endswith((".json", ".yaml", ".yml"))
                for f in os.listdir(local_guardrails_path)
                if os.path.isfile(os.path.join(local_guardrails_path, f))
            )
            if policy_files_exist:
                logger.debug(f"Using local policies directory: {local_guardrails_path}")
                return local_guardrails_path
            else:
                logger.debug(
                    f"Local directory '{local_guardrails_path}' exists but contains no policy files. Checking bundled policies."
                )

        # 3. Fallback to the bundled guardrails directory
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            bundled_policy_dir = os.path.join(current_dir, "guardrails")

            if os.path.isdir(bundled_policy_dir):
                # Check if it contains any policy files
                policy_files_exist = any(
                    f.lower().endswith((".json", ".yaml", ".yml"))
                    for f in os.listdir(bundled_policy_dir)
                    if os.path.isfile(os.path.join(bundled_policy_dir, f))
                )
                if policy_files_exist:
                    logger.debug(
                        f"Using bundled policies directory: {bundled_policy_dir}"
                    )
                    return bundled_policy_dir
                else:
                    logger.error(
                        f"Bundled policy directory exists but contains no policy files: {bundled_policy_dir}. Policy enforcement might not work correctly."
                    )
                    return bundled_policy_dir
            else:
                logger.error(
                    f"Bundled policies directory not found at expected location: {bundled_policy_dir}. Policy enforcement might not work correctly."
                )
                return bundled_policy_dir

        except Exception as e:
            logger.error(f"Error determining bundled policy path: {e}", exc_info=True)
            return os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "guardrails"
            )

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors.

        Returns:
            List[str]: List of validation error messages. Empty if valid.
        """
        errors = []

        # API key validation
        if self.api_key and not self.api_key.startswith("rizk_"):
            errors.append("API key must start with 'rizk_'")

        # Endpoint validation
        if self.opentelemetry_endpoint:
            if not self.opentelemetry_endpoint.startswith(("http://", "https://")):
                errors.append("OpenTelemetry endpoint must be a valid HTTP/HTTPS URL")

        # Policies path validation
        if self.policies_path and not os.path.exists(self.policies_path):
            errors.append(f"Policies path does not exist: {self.policies_path}")

        # Numeric validation
        if self.framework_detection_cache_size < 0:
            errors.append("Framework detection cache size must be non-negative")

        # App name validation
        if not self.app_name or not self.app_name.strip():
            errors.append("App name cannot be empty")

        return errors

    def is_valid(self) -> bool:
        """Check if configuration is valid.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        return len(self.validate()) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dict[str, Any]: Configuration as dictionary.
        """
        return {
            "app_name": self.app_name,
            "api_key": "***" if self.api_key else None,  # Mask sensitive data
            "opentelemetry_endpoint": self.opentelemetry_endpoint,
            "tracing_enabled": self.tracing_enabled,
            "trace_content": self.trace_content,
            "metrics_enabled": self.metrics_enabled,
            "logging_enabled": self.logging_enabled,
            "policies_path": self.policies_path,
            "policy_enforcement": self.policy_enforcement,
            "telemetry_enabled": self.telemetry_enabled,
            "lazy_loading": self.lazy_loading,
            "framework_detection_cache_size": self.framework_detection_cache_size,
            "debug_mode": self.debug_mode,
            "verbose": self.verbose,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "RizkConfig":
        """Create configuration from dictionary.

        Args:
            config_dict: Configuration dictionary.

        Returns:
            RizkConfig: Configuration instance.
        """
        # Get valid field names from the dataclass
        from dataclasses import fields

        valid_fields = {f.name for f in fields(cls)}

        # Filter the dictionary to only include valid fields
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_fields}

        return cls(**filtered_dict)

    @classmethod
    def from_env(cls, **overrides: Any) -> "RizkConfig":
        """Create configuration from environment variables with optional overrides.

        Args:
            **overrides: Override values for specific configuration fields.

        Returns:
            RizkConfig: Configuration instance.
        """
        config = cls()

        # Apply overrides
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                logger.warning(f"Unknown configuration override: {key}")

        return config


# Global configuration instance
_global_config: Optional[RizkConfig] = None


def get_config() -> RizkConfig:
    """Get the global configuration instance.

    Returns:
        RizkConfig: Global configuration instance.
    """
    global _global_config
    if _global_config is None:
        _global_config = RizkConfig.from_env()
    return _global_config


def set_config(config: RizkConfig) -> None:
    """Set the global configuration instance.

    Args:
        config: Configuration instance to set as global.
    """
    global _global_config
    _global_config = config


def reset_config() -> None:
    """Reset the global configuration to defaults."""
    global _global_config
    _global_config = None


# Backward compatibility functions - these delegate to the new centralized config
def is_tracing_enabled() -> bool:
    """Checks if Rizk OpenTelemetry tracing is enabled."""
    return get_config().tracing_enabled


def is_content_tracing_enabled() -> bool:
    """Checks if tracing the content (e.g., LLM prompts/responses) is enabled."""
    return get_config().trace_content


def is_metrics_enabled() -> bool:
    """Checks if Rizk metrics collection is enabled."""
    return get_config().metrics_enabled


def is_logging_enabled() -> bool:
    """Checks if Rizk SDK's internal logging is enabled."""
    return get_config().logging_enabled


def get_opentelemetry_endpoint() -> Optional[str]:
    """Gets the configured OpenTelemetry collector endpoint URL."""
    return get_config().opentelemetry_endpoint


def get_api_key() -> Optional[str]:
    """Gets the Rizk API key."""
    return get_config().api_key


def get_policies_path() -> str:
    """Determines the path to the guardrail policies directory or file."""
    config = get_config()
    # Since __post_init__ ensures policies_path is never None, we can safely assert this
    assert config.policies_path is not None, (
        "policies_path should be set by __post_init__"
    )
    return config.policies_path


def is_policy_enforcement_enabled() -> bool:
    """Checks if guardrail policy enforcement is globally enabled."""
    return get_config().policy_enforcement
