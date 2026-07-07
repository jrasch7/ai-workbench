# AIW Cockpit V2 — Validation and Next Steps

## Estado Git atual

- Branch de estabilização: `fix/aiw-cockpit-v2-stabilization`
- PR relevante já mergeado: PR #4 — `feat: redesign AIW cockpit as agent workspace`
- Merge commit remoto observado: `1ba596b`
- Branch original da V2: `feature/aiw-cockpit-agent-workspace-v2`
- Situação local observada:
  - `origin/main` já contém a V2 mergeada.
  - `main` local estava atrasada no momento do diagnóstico.
  - A branch original remota da V2 foi deletada após merge.
  - O Cockpit V2 existia localmente, mas `scripts/aiw-cockpit` estava sem bit executável.

## O que a V2 implementou de fato

A V2 transformou o cockpit de um painel técnico em um workspace de operação de agentes.

Implementado no `scripts/aiw-cockpit`:

- shell visual com sidebar;
- seções de workspace;
- overview;
- nova task;
- inbox;
- running;
- review;
- done;
- failed;
- models;
- docs;
- settings;
- composer central com a pergunta “O que você quer que o AIW faça?”;
- botão principal “Criar e executar com IA”;
- botão secundário “Salvar na inbox”;
- campo opcional de documentação;
- IA como padrão;
- seletor/dropdown de modelo;
- opções de modelo:
  - `dev-gemini-fast`;
  - `dev-coder`;
  - `dev-balanced`;
  - `dev-large`;
  - `dev-review`;
  - `dev-architect`;
- cards de inbox;
- cards de review;
- atividade recente;
- detalhe de run com layout próprio;
- botões de aprovar/rejeitar no fluxo de review.

## O que está funcionando

Validações já observadas:

- `./scripts/aiw doctor-local` passou com `AIW_DOCTOR_STATUS=OK`;
- scripts principais existem;
- diretórios `.aiw/tasks/*`, `.aiw/runs` e `.aiw/state` existem;
- LiteLLM respondeu no doctor;
- modelo `dev-gemini-fast` passou no smoke do doctor;
- `python3 -m py_compile scripts/aiw-cockpit` passou;
- `bash -n scripts/aiw` passou;
- Cockpit iniciou em porta isolada após corrigir permissão;
- home respondeu via HTTP;
- `/api/status` respondeu;
- `/api/runs` respondeu;
- tela contém os textos principais esperados da V2:
  - `AIW Cockpit`;
  - `O que você quer que o AIW faça?`;
  - `Criar e executar com IA`;
  - `Salvar na inbox`;
  - `Inbox`;
  - `Running`;
  - `Review`;
  - `Done`;
  - `Failed`;
  - `Models`;
  - `Docs`;
  - `Settings`;
  - `Atividade recente`;
  - modelos esperados.

## O que estava quebrado

### 1. `./scripts/aiw cockpit` não subia

Erro observado:

```text
./scripts/aiw: line 65: /home/joao/ai-workbench/scripts/aiw-cockpit: Permission denied

Causa:

scripts/aiw-cockpit estava versionado/checkout como 100644, sem permissão de execução.

Correção aplicada nesta estabilização:

chmod +x scripts/aiw-cockpit
2. Arquivos acidentais no root

Foram observados no diff da V2:

readme.txt;
readme.txt:Zone.Identifier.

Interpretação:

readme.txt parece contexto/handoff colado no repositório por acidente;
readme.txt:Zone.Identifier é lixo típico de arquivo vindo do Windows/Edge/Chrome/attachment.

Correção nesta estabilização:

remover ambos se estiverem rastreados pelo Git.
O que melhorou em relação ao Cockpit anterior

A V2 melhorou pontos essenciais:

deixou de parecer apenas um painel técnico;
passou a ter estrutura de workspace;
ganhou sidebar;
ganhou composer estilo ChatGPT/Claude;
removeu o checkbox “Usar LLM” do fluxo principal;
trocou modelo em texto livre por seletor;
tornou a inbox mais visual;
criou área de review mais humana;
aproximou o cockpit da ideia de operador de agentes;
deixou mais claro que o AIW executa com IA por padrão.
O que ainda está ruim

Ainda precisa evoluir:

O visual precisa de polish final para parecer produto consolidado, não só um HTML interno bonito.
A execução de task selecionada precisa ficar impossível de confundir.
O review ainda precisa resumir melhor:
objetivo;
resultado;
arquivo gerado;
risco;
próxima ação.
A tela de detalhe do run deve priorizar leitura humana antes dos detalhes técnicos.
Models/Docs/Settings ainda parecem seções placeholder ou secundárias.
Falta validar melhor os fluxos completos via UI:
criar task comum;
criar doc task;
salvar na inbox;
criar e executar com IA;
selecionar task da inbox;
aprovar/rejeitar run.
Comparação com a visão desejada
Devin

A V2 avança na direção correta porque cria um workspace de execução, mas ainda falta sensação de “agente trabalhando com progresso, plano e próxima ação”.

Claude/ChatGPT

O composer central já aproxima o cockpit desse padrão. Ainda precisa melhorar microcopy, estado vazio, feedback após envio e continuidade da conversa/tarefa.

Cursor / Antigravity Agent Manager

A sidebar e os estados de fila ajudam. Ainda falta uma visão mais clara de agentes/runs ativos, histórico acionável e relação entre task → run → resultado.

Paperclip

A V2 ainda não é um control plane de agentes, mas já cria uma base visual para cockpit operacional. Paperclip deve continuar como inspiração futura, não como dependência agora.

AI Operator Workspace

A V2 já é o primeiro corte real de AI Operator Workspace. O próximo passo não é recomeçar: é estabilizar e polir em slices.

Próxima frente recomendada

Recomendação: UX polish focado, não refatoração grande agora.

Ordem recomendada:

Estabilizar esta correção:
permissão executável;
limpeza de arquivos acidentais;
documento de validação.
Fazer uma rodada curta de UX polish:
melhorar cards de inbox;
melhorar card de task selecionada;
melhorar review;
melhorar detalhe de run;
melhorar empty states;
melhorar feedback pós-ação.
Só depois pensar em arquitetura maior:
daemon;
agentes nomeados;
Paperclip;
Go/Rust;
runner mais robusto.
Critério de aceite imediato

O cockpit precisa permitir que o usuário entenda rapidamente:

onde digitar o que quer;
qual modelo será usado;
se vai salvar ou executar;
qual task será executada;
o que está aguardando revisão;
qual ação tomar em seguida.

Status atual: parcialmente atingido.

A base V2 está boa o suficiente para avançar com polish, desde que a correção de permissão e a limpeza sejam mergeadas.
