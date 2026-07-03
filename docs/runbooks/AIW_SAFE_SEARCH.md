# AIW Safe Search Guard v1

## Objetivo

`scripts/aiw-safe-search` existe para substituir buscas manuais perigosas como `grep -R "..." -n .` quando houver risco de varrer secrets ou artifacts locais.

O problema operacional que motivou este guard foi repetido: comandos com `grep` mal cotados em ambientes PowerShell/WSL podem interpretar `|` ou aspas de forma inesperada e transformar uma busca escopada em busca ampla.

## Uso Correto

```bash
./scripts/aiw-safe-search "isolation_profile" --paths aiw_workspace docs/runbooks README.md
```

O output usa paths relativos ao repo:

```text
path:line:conteudo
```

Exit codes:

```text
0 encontrou
1 nao encontrou
2 uso invalido ou bloqueado
```

## Exemplos Permitidos

```bash
./scripts/aiw-safe-search "aiw-safe-search" --paths scripts docs/runbooks README.md
./scripts/aiw-safe-search "stronger_isolation_required" --paths aiw_workspace docs/runbooks
./scripts/aiw-safe-search "grep -R" --paths docs/runbooks README.md
```

## Exemplos Bloqueados

Sem paths:

```bash
./scripts/aiw-safe-search "isolation_profile"
```

Busca ampla:

```bash
./scripts/aiw-safe-search "isolation_profile" --paths .
```

Path absoluto:

```bash
./scripts/aiw-safe-search "anything" --paths /home/joao/ai-workbench
```

Traversal:

```bash
./scripts/aiw-safe-search "anything" --paths ../ai-workbench
```

Secrets e instrucoes sensiveis:

```bash
./scripts/aiw-safe-search "anything" --paths .env
./scripts/aiw-safe-search "anything" --paths config/litellm.yaml
./scripts/aiw-safe-search "anything" --paths AGENTS.md
```

Artifacts e dependencias:

```bash
./scripts/aiw-safe-search "anything" --paths .aiw
./scripts/aiw-safe-search "anything" --paths .git
./scripts/aiw-safe-search "anything" --paths node_modules
```

## Regras

A ferramenta:

- exige termo de busca;
- exige `--paths`;
- recusa `.` e paths absolutos;
- recusa paths que resolvem para fora do repo;
- recusa `..` em paths recebidos, mesmo quando resolveriam de volta para o repo;
- recusa `.env`, `config/litellm.yaml` e `AGENTS.md` antes de leitura;
- recusa `.git`, `.aiw`, `reports`, `coverage`, `logs`, `node_modules`, `.venv`, `venv` e `__pycache__`;
- busca somente nos paths explicitamente passados;
- nao imprime binarios;
- ignora arquivos acima de 1 MB;
- trunca linhas muito longas.

## Limites

Este guard nao e scanner de seguranca e nao substitui revisao humana. Ele reduz erro operacional em buscas textuais, mas ainda depende de escopo bem escolhido pelo operador.

Regra para agentes: use `scripts/aiw-safe-search` em vez de `grep -R` sempre que houver risco de varrer secrets, artifacts locais ou diretórios amplos.
