# AIW File OS Phase 3D

## Resultado

Implementação concluída e APROVADA. As ferramentas restritas de File OS foram disponibilizadas para uso pelo Agent de modo controlado, evitando path traversal e limitando as zonas de gravação (allowlisting).

## Tools adicionadas

- `file_write`
- `file_patch`

## Política de segurança

- Path absolutos bloqueados.
- Uso de caracteres de escape de diretórios (`..`) bloqueado.
- Bloqueio sumário a diretórios vitais do projeto: `.git/`, `.venv/`, `node_modules/`, `vendor/`, `__pycache__/`.
- Restrição preventiva em extensões binárias (.exe, .so, .dll, .jpg, .png, etc).
- Rejeição na alteração ou criação de arquivos que contenham nomes sensíveis (ex: `.env`, `secret`, `token`, `credential`, `private_key`, `client_secret`).

## Paths permitidos

Por padrão, a escrita de novos arquivos ou substituição de conteúdo é permitida apenas em caminhos considerados seguros na raiz do workspace ou em seus subdiretórios configurados para gravação pelo bot:
- `docs/`
- `reports/`
- `.aiw/generated/`
- `.aiw/runs/`

Qualquer outra escrita ou sobreposição explícita em arquivos essenciais bloqueia com exceção, retornando status legível ao LLM.

## Backups

Tanto `file_write` (com `overwrite=true` em arquivos existentes) quanto `file_patch` acionam o backup autônomo. Uma cópia do arquivo original é movida de imediato para a hierarquia `.aiw/backups/<timestamp>/...` e o caminho do arquivo assegurado retorna nas evidências do trace (`backup_path`).

## Contratos JSON

### file_write
```json
{
  "path": ".aiw/generated/exemplo.md",
  "content": "conteúdo de texto\n",
  "overwrite": true
}
```

### file_patch
```json
{
  "path": ".aiw/generated/exemplo.md",
  "old_text": "texto_antigo",
  "new_text": "texto_novo",
  "expected_replacements": 1
}
```

## Validações executadas

- `bash -n scripts/aiw-runner-agent`, `scripts/aiw-tool-smoke` e `scripts/aiw-cockpit`: Sintaxe dos blocos heredocs confirmada.
- Check python compilation com module runner: Limpo.
- Testes diretos simulando CLI commands nas tools.
- Smoke tool via bash script.
  - Tests para success: Aprovados nas paths corretas.
  - Tests para fallbacks/exceptions: Disparos com path fora da boundary, `.env` file target, substituição regex em branch inválida falharam de modo antecipado retornando JSON amigável `ok: False`, travando com sucesso exploração desautorizada.

## Evidências

- Adição de novos esquemas validados presentes na lista `TOOLS` enviadas pro LiteLLM na classe `run_agent()`.
- O smoke script validou dezenas de ramificações, atestando backups automáticos e retornos precisos do path traversal blocking mechanism.

## Limitações

- `file_patch` usa substituição exata (find and replace literal na string do arquivo todo).
- Sem regex patch (por segurança).
- Sem patch difuso/fuzzy.
- Sem escrita fora da allowlist base do File OS restrito.
- Sem integração Hermes (arquitetura totalmente nativa para cockpit local).
- Sem shell irrestrito (comandos permanecem no modelo de allowlist).

## Próximo passo recomendado

Revisão visual e QA de uso real na interface e commits na esteira principal `origin/main`. Recomendada próxima implementação a Fase 3D.2 de leitura fuzzy se julgar os patches insuficientes ou seguir rumo à customização do File Interface Dashboard do próprio cockpit para observar a árvore de `.aiw/backups` na UI.
