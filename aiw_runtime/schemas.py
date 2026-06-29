DIRECTORY_LIST_SCHEMA = {
    "type": "function",
    "function": {
        "name": "directory_list",
        "description": "Lista o conteúdo de um diretório respeitando o escopo do workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Caminho relativo ao repo (ex: '.')"},
                "max_depth": {"type": "integer", "description": "Profundidade máxima", "default": 2},
                "limit": {"type": "integer", "description": "Limite de entradas retornadas", "default": 100}
            },
            "required": ["path"]
        }
    }
}

FILE_READ_SCHEMA = {
    "type": "function",
    "function": {
        "name": "file_read",
        "description": "Retorna o conteúdo de um arquivo em texto.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Caminho do arquivo relativo ao repo"},
                "max_bytes": {"type": "integer", "description": "Máximo de bytes para leitura", "default": 8000}
            },
            "required": ["path"]
        }
    }
}

SHELL_EXEC_SCHEMA = {
    "type": "function",
    "function": {
        "name": "shell_exec",
        "description": "Executa comandos restritos no sandbox local.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Comando para executar"},
                "timeout": {"type": "integer", "description": "Timeout máximo (<=30)", "default": 20}
            },
            "required": ["command"]
        }
    }
}

FILE_WRITE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "file_write",
        "description": "Cria ou sobrescreve um arquivo (permitido apenas em caminhos autorizados).",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Caminho relativo ao repo"},
                "content": {"type": "string", "description": "Conteúdo do arquivo"},
                "overwrite": {"type": "boolean", "description": "Se verdadeiro, cria backup e sobrescreve", "default": False}
            },
            "required": ["path", "content"]
        }
    }
}

FILE_PATCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "file_patch",
        "description": "Substitui um texto exato em um arquivo (permitido apenas em caminhos autorizados).",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Caminho relativo ao repo"},
                "old_text": {"type": "string", "description": "Texto exato a ser substituído"},
                "new_text": {"type": "string", "description": "Novo texto"},
                "expected_replacements": {"type": "integer", "description": "Quantidade exata de ocorrências esperadas", "default": 1}
            },
            "required": ["path", "old_text", "new_text", "expected_replacements"]
        }
    }
}

PROJECT_PATCH_PREVIEW_SCHEMA = {
    "type": "function",
    "function": {
        "name": "project_patch_preview",
        "description": "Cria uma proposta de alteração em código-fonte. A alteração não é aplicada imediatamente; requer aprovação posterior (apply).",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Caminho relativo ao repo"},
                "old_text": {"type": "string", "description": "Texto exato a ser substituído"},
                "new_text": {"type": "string", "description": "Novo texto"},
                "expected_replacements": {"type": "integer", "description": "Quantidade exata de ocorrências esperadas", "default": 1},
                "reason": {"type": "string", "description": "Explicação curta sobre a mudança"}
            },
            "required": ["path", "old_text", "new_text", "expected_replacements", "reason"]
        }
    }
}

PROJECT_PATCH_APPLY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "project_patch_apply",
        "description": "Aplica uma proposta de patch (preview) gerada por project_patch_preview.",
        "parameters": {
            "type": "object",
            "properties": {
                "patch_id": {"type": "string", "description": "O ID do patch gerado."}
            },
            "required": ["patch_id"]
        }
    }
}

PROJECT_PATCH_ROLLBACK_SCHEMA = {
    "type": "function",
    "function": {
        "name": "project_patch_rollback",
        "description": "Desfaz (rollback) um patch que já foi aplicado via project_patch_apply, restaurando o backup gerado.",
        "parameters": {
            "type": "object",
            "properties": {
                "patch_id": {"type": "string", "description": "O ID do patch aplicado."}
            },
            "required": ["patch_id"]
        }
    }
}

TOOLS = [
    DIRECTORY_LIST_SCHEMA,
    FILE_READ_SCHEMA,
    SHELL_EXEC_SCHEMA,
    FILE_WRITE_SCHEMA,
    FILE_PATCH_SCHEMA,
    PROJECT_PATCH_PREVIEW_SCHEMA,
    PROJECT_PATCH_APPLY_SCHEMA,
    PROJECT_PATCH_ROLLBACK_SCHEMA
]
