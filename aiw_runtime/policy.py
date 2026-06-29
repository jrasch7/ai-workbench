import os
from pathlib import Path
import shlex

def get_root() -> Path:
    return Path(os.environ.get("AIW_ROOT", Path.cwd())).resolve()

def validate_path(path_str: str) -> Path:
    """Bloquear path absoluto, escape por .., e arquivos sensíveis como .env."""
    root = get_root()
    path = Path(path_str)
    
    if path.is_absolute():
        raise ValueError("Path absoluto bloqueado.")
    
    # Resolve relative to root
    resolved = (root / path).resolve()
    
    try:
        resolved.relative_to(root)
    except ValueError:
        raise ValueError("Escape de diretório bloqueado (..).")
    
    if resolved.name == ".env" or ".env." in resolved.name:
        raise ValueError("Acesso a .env bloqueado.")
        
    return resolved

def validate_shell_command(command_str: str) -> list[str]:
    """
    bloquear operadores: ;, &&, ||, |, >, <, backtick, $(;
    bloquear .env, secret, token, credential, private_key, client_secret;
    permitir inicialmente apenas uma allowlist de comandos.
    """
    # Simple substring blocks
    blocked_chars = [';', '&&', '||', '|', '>', '<', '`', '$(']
    for c in blocked_chars:
        if c in command_str:
            raise ValueError(f"Operador perigoso bloqueado: {c}")
            
    blocked_words = ['.env', 'secret', 'token', 'credential', 'private_key', 'client_secret']
    lower_cmd = command_str.lower()
    for w in blocked_words:
        if w in lower_cmd:
            raise ValueError(f"Palavra sensível bloqueada: {w}")

    # Parse command safely
    parts = shlex.split(command_str)
    if not parts:
        raise ValueError("Comando vazio.")
        
    base_cmd = parts[0]
    allowed_bases = ["pwd", "ls", "find", "cat", "sed", "grep", "head", "tail", "git", "bash", "python3"]
    
    if base_cmd not in allowed_bases:
        raise ValueError(f"Comando não autorizado: {base_cmd}")
        
    if base_cmd == "git":
        if len(parts) > 1:
            sub = parts[1]
            allowed_git = ["status", "diff", "log", "show", "branch", "rev-parse"]
            if sub not in allowed_git:
                raise ValueError(f"Subcomando git mutável bloqueado: {sub}")
    elif base_cmd == "bash":
        if len(parts) < 2 or parts[1] != "-n":
            raise ValueError("bash só é permitido com -n")
    elif base_cmd == "python3":
        if len(parts) < 3 or parts[1] != "-m" or parts[2] not in ["py_compile", "compileall"]:
            raise ValueError("python3 só é permitido para py_compile ou compileall")
            
    return parts
