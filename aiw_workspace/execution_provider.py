# MIGRAÇÃO CIRÚRGICA (Cockpit + Loop Iterativo do Agente): 
# aiw_workspace/execution_provider.py agora thin delegate para aiw/providers/execution.
# A classe CodeActExecutionProvider e lógica migraram (ver codeact.py).
# Mantém compatibilidade. Termos PT: Provedor de Execução.
# (Evita duplicação; não migra módulos pesados não relacionados.)

from aiw.providers.execution import (
    CodeActExecutionProvider,
    list_execution_providers,
    get_execution_provider,
    describe_execution_provider,
    validate_execution_provider,
)

# Símbolos legados para compat
CODEACT_PROVIDER_NAME = "codeact"
EXECUTION_PROVIDER_VERSION = "execution_provider_v1"

# RUNTIME_PROFILE reexport (definido em runtime_gate; bridge de compat)
from .runtime_gate import RUNTIME_PROFILE


# CODEACT_SUPPORTED_OPERATIONS e duplicatas removidas (agora via aiw/ import)
# Mantido apenas para referência de compat se necessário em runtime.


# (classe CodeActExecutionProvider agora vem via import do aiw/ acima - thin delegate)
# Stub para _fixed se algum caller legado referenciar diretamente (mantém compat sem duplicar lógica)
def _fixed_probe_action() -> dict:
    return {
        "kind": "python_eval",
        "title": "AIW Execution Provider Validation Probe",
        "code": "print('AIW_EXECUTION_PROVIDER_PROBE_OK')",
        "timeout_seconds": 5,
        "max_stdout_chars": 2000,
        "max_stderr_chars": 2000,
    }


# list_execution_providers() reexportado do aiw/ no topo (thin delegate)
# Def antiga removida.

# get_execution_provider etc fornecidos pelo reexport 'from aiw.providers.execution' (thin delegate cirúrgico)
# Removidas as implementações duplicadas.

def provider_for_capability(capability_name: str, exec_provider_name: str = None):
    """Thin delegate para o bridge de Provedores de Execução em aiw/."""
    from aiw.providers.execution.bridge import provider_for_capability as fn
    return fn(capability_name, exec_provider_name)

# Fim da atualização para execution_provider.py - foco em Cockpit + agent path.
