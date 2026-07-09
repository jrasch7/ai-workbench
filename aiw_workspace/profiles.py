# MIGRAÇÃO CIRÚRGICA: Lógica pesada de workspace profiles movida para aiw/workspace/profiles.py
# Este arquivo agora é thin delegate reexportando de aiw/ (aiw-first).
# Mantém compatibilidade total para callers legados (aiw_workspace.*, cockpit, aiw/patch/*, etc).
# Prefer: from aiw.workspace.profiles import ... ou from aiw import load_workspaces_config, resolve_workspace, validate_profile etc.
#
# Também mantém reexports cirúrgicos para Agent Profiles (de aiw/profiles/loader) para compat total.
# Sem mudanças de lógica.

import json
import re
import shlex
import subprocess
from pathlib import Path

# Reexport agent profile symbols para compat total em callers que ainda importam de aiw_workspace.profiles.
# Fonte da verdade: aiw/profiles/loader.py
try:
    from aiw.profiles.loader import load_profile as load_agent_profile, get_profile as get_agent_profile, list_profiles as list_agent_profiles
except Exception:
    load_agent_profile = None
    get_agent_profile = None
    list_agent_profiles = None

# Reexport workspace profiles pesados agora de aiw/ primary
from aiw.workspace.profiles import (
    AIW_ROOT,
    DEFAULT_PROFILE,
    DEFAULT_WORKSPACE,
    normalize_workspace_id,
    load_workspaces_config,
    resolve_workspace,
    execution_policy,
    validate_workspace_path,
    detect_stack,
    profile_for_stack,
    validate_test_command,
    validate_test_mappings,
    validate_validation_groups,
    validate_profile,
    add_workspace,
    remove_workspace,
)

# Reexports cirúrgicos para Agent Profiles (impactam Cockpit + aiw/agent/loop path).
# Permite from aiw_workspace.profiles import load_agent_profile etc durante transição (sem big-bang).
if load_agent_profile is not None:
    # expõe com nomes canônicos também para compat legada que esperava "load_profile" para agent
    load_profile = load_agent_profile
    get_profile = get_agent_profile
    list_profiles = list_agent_profiles
else:
    load_profile = None
    get_profile = None
    list_profiles = None

__all__ = [
    # workspace profiles (agora delegados de aiw/workspace/profiles.py)
    "load_workspaces_config", "resolve_workspace", "add_workspace", "remove_workspace",
    "normalize_workspace_id", "validate_profile", "profile_for_stack",
    "execution_policy", "validate_workspace_path", "detect_stack", "validate_test_command",
    "validate_test_mappings", "validate_validation_groups",
    "DEFAULT_PROFILE", "DEFAULT_WORKSPACE", "AIW_ROOT",
    # agent profiles (migrados, reexport para path cockpit/agent)
    "load_agent_profile", "get_agent_profile", "list_agent_profiles",
    "load_profile", "get_profile", "list_profiles",
]

# Fim da migração para profiles (aiw/workspace primary + compat).
