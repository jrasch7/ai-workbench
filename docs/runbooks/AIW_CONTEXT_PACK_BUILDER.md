# AIW Context Pack Builder v1

Este runbook detalha o funcionamento do **Context Pack Builder v1**, o mecanismo que orquestra a criação de pacotes de contexto úteis, compactos e auditáveis para os agentes de IA operarem no repositório local.

## O que é um Context Pack?

Um Context Pack é um "pacote de conhecimento" estático e finito. Em vez de injetar o repositório inteiro na janela de contexto de um modelo de linguagem (LLM) – o que resultaria em alto custo, lentidão e dispersão da IA –, o Builder usa buscas (léxicas na v1) para recortar "chunks" de código específicos baseados na demanda da tarefa atual. 

## Como usa o índice local

O Context Pack Builder baseia-se diretamente no índice local gerado pela Capability `AIW-CAP-02` (RAG Index). Ele passa os termos principais extraídos do objetivo da task (via query ou text) para a engine de busca. Ela retorna os trechos de arquivos já processados pelo chunker, sem que o Builder precise reler arquivos brutos.

## Como funciona o Orçamento de Contexto (Budget)

A geração do pack respeita rigidamente dois limites:
- `max_chunks`: Número máximo de segmentos textuais a incluir (ex: 8, 12).
- `max_chars`: Quantidade de caracteres absolutos somados entre os chunks (ex: 24000).

Se uma busca retornar 100 resultados, o Builder irá varrê-los do mais relevante (score mais alto) para o menor, somando seus caracteres. No momento em que atingir `max_chars` ou `max_chunks`, ele para de incluir novos chunks. 
Se um único chunk, por qualquer motivo, ultrapassar `max_chars`, ele será truncado antes da inclusão.

## Como rodar o Context Pack Builder isoladamente

É possível acionar o script via CLI informando a `query` (termos a pesquisar) e os limites de chunking e chars:

```bash
python3 -m aiw_context.context_pack --workspace aiw --query "agent dispatcher" --max-chunks 8 --max-chars 24000
```

## Onde ficam os artefatos gerados?

Todo Context Pack é gravado de forma imutável e auditável em:
`.aiw/workspaces/<workspace_id>/context-packs/<pack_id>/`

Sendo formados por:
- `context-pack.json`: Representação programática consumível pelo Runtime. Inclui source metadata, chunks, estatísticas de uso (tokens estimados e limits).
- `context-pack.md`: Visualização Human-Readable e AI-Readable do contexto. É esse Markdown concatenado que será efetivamente passado na prompt-chain do agente em execuções CodeAct.

## Como auditar os chunks selecionados

Basta abrir o arquivo `.aiw/workspaces/<workspace_id>/context-packs/<pack_id>/context-pack.md` para inspecionar visualmente se os chunks selecionados fazem sentido e se não carregam lixo indesejado. É vital para avaliar o nível de utilidade da técnica de recuperação.

## Como será usado pelo Agent Runner no futuro

Quando o Agent Loop (`AIW-CAP-06`) for ativado, antes de iniciar o planejamento e a primeira delegação de tool para o LLM, o Agent Dispatcher solicitará à Capability Layer a criação de um Context Pack. O Agent injetará o `.md` retornado nas `system messages` para basear a inteligência, permitindo atuar imediatamente sem "tatear" o repositório cegamente.

## Por que ainda não usa embeddings/Ollama?

Manter o fallback puramente local (léxico) valida o fluxo de empacotamento, budgeting e injeção sem a complexidade adicional e opacidade de bancos de vetores ou dependência de contêineres de modelos rodando por trás. Quando Ollama for introduzido, apenas a função de "pesquisa" muda para busca semântica, mas a interface e o budget do pack continuam exatamente os mesmos.

## Limitações da v1

- **Busca cega a jargões puros**: A busca léxica não entende semântica. 
- **Fragmentação abrupta**: O chunking fatiado cegamente por limite de linha/char pode quebrar funções ao meio. Code-aware chunking (AST) é uma evolução mapeada.
