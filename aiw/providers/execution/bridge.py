"""Bridge functions for migration.

Permite código antigo usar o registro novo gradualmente.
Migração em andamento para formato aiw/.
"""

from aiw.providers.execution.registry import get_execution_provider_registry


def provider_for_capability(capability_name: str, exec_provider_name: str = None):
    """Bridge para o registry atualizado.

    Suporta preferência execution_provider do Perfil.
    """
    registry = get_execution_provider_registry()
    name = exec_provider_name or "codeact"
    provider = registry.get(name)
    if provider:
        if isinstance(provider, type):
            provider = provider()
        if capability_name == "codeact_sandbox":
            return provider
    # Fallback direto (agora do aiw/ migrado, sem aiw_workspace para o caminho do agente)
    from .codeact import CodeActExecutionProvider
    if capability_name == "codeact_sandbox":
        return CodeActExecutionProvider()
    return None
