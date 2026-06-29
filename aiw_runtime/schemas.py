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

TOOLS = [DIRECTORY_LIST_SCHEMA, FILE_READ_SCHEMA, SHELL_EXEC_SCHEMA]
