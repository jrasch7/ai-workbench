import json
from .test_runner import load_patch_preview

def is_test_file(path: str) -> bool:
    lower_path = path.lower()
    parts = lower_path.split("/")
    name = parts[-1]
    
    if "test" in parts or "tests" in parts:
        return True
    
    if name.startswith("test_"):
        return True
        
    if name.endswith("_test.py"):
        return True
        
    test_suffixes = (".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".test.js", ".spec.js")
    if name.endswith(test_suffixes):
        return True
        
    return False

def is_docs_file(path: str) -> bool:
    lower_path = path.lower()
    if lower_path.endswith(".md"):
        return True
    if lower_path == "readme.md":
        return True
    if "docs/" in path or path.startswith("docs/"):
        return True
    return False

def is_config_file(path: str) -> bool:
    lower_path = path.lower()
    config_exts = (".json", ".yaml", ".yml", ".toml", ".ini", ".cfg")
    if lower_path.endswith(config_exts):
        return True
    name = lower_path.split("/")[-1]
    if name in ("dockerfile", "docker-compose.yml"):
        return True
    return False

def is_code_file(path: str) -> bool:
    lower_path = path.lower()
    code_exts = (".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".cs")
    if lower_path.endswith(code_exts):
        return True
    if lower_path.startswith("scripts/") or "/scripts/" in lower_path:
        return True
    return False

def analyze_test_coverage_intent(workspace_id: str, patch_id: str, patch_payload_override: dict = None) -> dict:
    if patch_payload_override:
        patch_payload = patch_payload_override
    else:
        patch_payload = load_patch_preview(workspace_id, patch_id)
        
    if not patch_payload.get("ok"):
        return {"ok": False, "error": patch_payload.get("error", "patch_not_found")}
        
    patch = patch_payload.get("patch", {})
    changed_files = patch.get("changed_files", [])
    
    tests = []
    codes = []
    docs = []
    configs = []
    others = []
    
    for f in changed_files:
        if is_test_file(f):
            tests.append(f)
        elif is_code_file(f):
            codes.append(f)
        elif is_docs_file(f):
            docs.append(f)
        elif is_config_file(f):
            configs.append(f)
        else:
            others.append(f)
            
    has_codes = len(codes) > 0
    has_tests = len(tests) > 0
    has_docs = len(docs) > 0
    has_configs = len(configs) > 0
    has_others = len(others) > 0
    
    categories_present = sum([has_codes, has_tests, has_docs, has_configs, has_others])
    
    if categories_present == 1:
        if has_codes:
            classification = "code_without_tests"
        elif has_tests:
            classification = "tests_only"
        elif has_docs:
            classification = "docs_only"
        elif has_configs:
            classification = "config_only"
        else:
            classification = "mixed"
    elif categories_present == 2 and has_codes and has_tests:
        classification = "code_with_tests"
    elif categories_present == 0:
        classification = "docs_only" # fallback for empty
    else:
        classification = "mixed"
        
    missing_test_signal = False
    
    if classification == "code_without_tests":
        severity = "warning"
        summary = "Patch altera código, mas não altera testes."
        missing_test_signal = True
    elif classification == "code_with_tests":
        severity = "none"
        summary = "Patch altera código e também altera testes."
    elif classification == "tests_only":
        severity = "info"
        summary = "Patch altera apenas arquivos de teste."
    elif classification == "docs_only":
        severity = "none"
        summary = "Patch altera apenas documentação."
    elif classification == "config_only":
        severity = "info"
        summary = "Patch altera apenas arquivos de configuração."
    else: # mixed
        if has_codes and not has_tests:
            severity = "warning"
            summary = "Patch misto contém código mas não contém testes."
            missing_test_signal = True
        elif has_codes and has_tests:
            severity = "info"
            summary = "Patch misto contém código e testes."
        else:
            severity = "info"
            summary = "Patch altera múltiplas categorias sem código."

    recommendations = []
    if missing_test_signal:
        recommendations.append("Rodar Validation Plan antes de aplicar o patch.")
        
    return {
        "ok": True,
        "workspace_id": workspace_id,
        "patch_id": patch_id,
        "classification": classification,
        "changed_code_files": codes,
        "changed_test_files": tests,
        "changed_docs_files": docs,
        "changed_config_files": configs,
        "missing_test_signal": missing_test_signal,
        "severity": severity,
        "summary": summary,
        "recommendations": recommendations
    }
