"""Simple Agent Profile loader.

Supports built-in profiles and basic workspace overrides.
Aligned to architecture.
"""

from typing import Any, Dict, Optional
import json
from pathlib import Path


# Built-in default profiles (aligned with vision)
BUILTIN_PROFILES: Dict[str, Dict[str, Any]] = {
    "software-engineer": {
        "name": "software-engineer",
        "display_name": "Software Engineer",
        "default_model": "dev-coder",
        "allowed_model_providers": ["openrouter", "litellm"],
        "temperature": 0.2,
        "tools": ["file_read", "file_write", "codeact_sandbox", "web_search", "git_log", "git_diff"],
        "default_capability": "codeact_sandbox",
        "default_operation": "python_eval_fixed",
        "execution_provider": "codeact",
        "allowed_execution_providers": ["codeact", "docker", "devcontainer"],
        "llm_planning_allowed": True,
        "context_strategy": "context-pack",
        "context_provider": "local_rag",
    },
    "security-analyst": {
        "name": "security-analyst",
        "display_name": "Security Analyst",
        "default_model": "dev-coder",
        "allowed_model_providers": ["openrouter", "litellm"],
        "temperature": 0.1,
        "tools": ["file_read", "codeact_sandbox", "web_search", "git_log", "git_diff"],
        "default_capability": "codeact_sandbox",
        "default_operation": "python_eval_fixed",
        "execution_provider": "codeact",
        "allowed_execution_providers": ["codeact", "docker", "devcontainer"],
        "llm_planning_allowed": True,
        "context_strategy": "context-pack",
        "context_provider": "local_rag",
    },
    "code-reviewer": {
        "name": "code-reviewer",
        "display_name": "Code Reviewer",
        "default_model": "dev-coder",
        "allowed_model_providers": ["openrouter", "litellm"],
        "temperature": 0.0,
        "tools": ["file_read", "git_diff"],
        "default_capability": "file_read",
        "default_operation": "file_read_operation",
        "execution_provider": "codeact",
        "allowed_execution_providers": ["codeact"],
        "llm_planning_allowed": False,
        "context_strategy": "context-pack",
        "context_provider": "local_rag",
    },
}


def load_profile(name: str, workspace_id: Optional[str] = None) -> Dict[str, Any]:
    """Load a profile, with optional workspace override."""
    profile = BUILTIN_PROFILES.get(name, BUILTIN_PROFILES["software-engineer"].copy())

    if workspace_id:
        # Future: load from workspace config
        pass

    return profile


def get_profile(name: str) -> Dict[str, Any]:
    return load_profile(name)


def list_profiles() -> list[str]:
    return list(BUILTIN_PROFILES.keys())
