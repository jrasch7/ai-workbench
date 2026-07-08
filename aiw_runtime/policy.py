import os
from pathlib import Path
import shlex

def get_root() -> Path:
    return Path(os.environ.get("AIW_WORKSPACE_ROOT") or os.environ.get("AIW_ROOT", Path.cwd())).resolve()

def get_aiw_root() -> Path:
    return Path(os.environ.get("AIW_ROOT", Path.cwd())).resolve()

def get_source_roots() -> list[str]:
    raw = os.environ.get("AIW_SOURCE_ROOTS", "")
    if raw.strip():
        return [p.strip() for p in raw.split(":") if p.strip()]
    return ["aiw_runtime", "scripts", "tests", "docs", ".aiw/generated", ".aiw/generated/tool-smoke"]

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

    blocked_names = {".env", ".git", ".venv", "node_modules", "vendor", "__pycache__"}
    for part in resolved.relative_to(root).parts:
        if part in blocked_names or part.startswith(".env."):
            raise ValueError(f"Acesso bloqueado: {part}")
    lower_path = str(resolved.relative_to(root)).lower()
    for word in ("secret", "token", "credential", "private_key", "client_secret"):
        if word in lower_path:
            raise ValueError(f"Acesso a caminho sensível bloqueado: {word}")

    return resolved

def _validate_common_write(resolved: Path, allowed_top_levels: list[str]) -> Path:
    root = get_root()
    rel = resolved.relative_to(root)

    # Bloquear nomes ou pastas sensíveis
    blocked_keywords = ['secret', 'token', 'credential', 'private_key', 'client_secret']
    lower_name = resolved.name.lower()
    for w in blocked_keywords:
        if w in lower_name:
            raise ValueError(f"Acesso a arquivo sensível bloqueado: {w}")

    parts = rel.parts
    if parts:
        top_level = parts[0]
        blocked_dirs = {".git", ".venv", "node_modules", "vendor", "__pycache__"}
        if top_level in blocked_dirs:
            raise ValueError(f"Escrita bloqueada no diretório protegido: {top_level}")

        # Permitir apenas diretórios seguros configurados
        allowed = False
        if top_level in allowed_top_levels:
            allowed = True
        # Casos especiais de subdiretório
        elif top_level == ".aiw" and len(parts) > 1 and parts[1] in ["generated", "runs"]:
            if ".aiw/generated" in allowed_top_levels or ".aiw/runs" in allowed_top_levels or ".aiw/*" in allowed_top_levels:
                allowed = True

        if not allowed:
            raise ValueError(f"Escrita não autorizada fora dos diretórios permitidos ({', '.join(allowed_top_levels)}).")

    # Bloquear arquivos binários por extensão (básico)
    binary_exts = {".jpg", ".png", ".gif", ".pdf", ".exe", ".bin", ".so", ".dll", ".pyc", ".zip", ".tar", ".gz"}
    if resolved.suffix.lower() in binary_exts:
        raise ValueError("Escrita em arquivos binários bloqueada.")

    return resolved

def validate_write_path(path_str: str) -> Path:
    """Bloqueios adicionais para file_write/file_patch em áreas seguras."""
    resolved = validate_path(path_str)
    allowed = ["docs", "reports", ".aiw/*"]
    return _validate_common_write(resolved, allowed)

def validate_project_patch_path(path_str: str) -> Path:
    """Bloqueios para project_patch_preview (código-fonte controlado)."""
    resolved = validate_path(path_str)
    allowed = get_source_roots()
    return _validate_common_write(resolved, allowed)

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
            allowed_git = ["status", "diff", "log", "show", "branch", "rev-parse", "checkout"]
            if sub not in allowed_git:
                raise ValueError(f"Subcomando git mutável bloqueado: {sub}")
    elif base_cmd == "bash":
        if len(parts) < 2 or parts[1] != "-n":
            raise ValueError("bash só é permitido com -n")
    elif base_cmd == "python3":
        if len(parts) < 3 or parts[1] != "-m" or parts[2] not in ["py_compile", "compileall"]:
            raise ValueError("python3 só é permitido para py_compile ou compileall")

    return parts
