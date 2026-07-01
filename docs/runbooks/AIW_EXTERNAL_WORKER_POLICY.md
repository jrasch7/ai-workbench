# AIW External Worker Policy

## Visão Geral

A camada de política local para **External Workers** do AI Workbench define rigidamente o que workers que interagem com serviços externos (como GitHub, Jira, etc.) têm permissão de fazer, onde e como.

## Propósito

Por motivos de segurança e estabilidade, o AIW foi desenhado inicialmente como uma bancada estritamente offline (sem background workers invisíveis alterando repositórios e abrindo pull requests). Para dar o próximo passo rumo ao *Continuous Agent Workflow*, criamos uma barreira (Policy) que autoriza gradualmente a operação.

Essa política garante que:
1. Saibamos exatamente "Quais workers existem".
2. Se podem rodar em "background" ou pela "UI".
3. Quais "ações" são permitidas (ex: criar PR, comentar issue) e quais são estritamente bloqueadas.

## Configuração Segura (Defaults)

Os defaults da política, quando não configurados explicitamente no profile, são os mais seguros possíveis:

```json
"external_workers": {
  "enabled": false,
  "allow_background": false,
  "allow_ui_execution": false,
  "workers": []
}
```

Isso significa que, sem configuração ativa:
- **Nenhum** webhook dispara daemon local;
- **Nenhuma** execução pela interface de usuário (UI) pode enviar comandos de edição para o GitHub;
- Tudo fica relegado à **CLI manual**.

## Estrutura de Workers

Um worker é configurado assim:

```json
{
  "name": "github_pr_edit",
  "target": "github",
  "mode": "manual_cli_only",
  "enabled": true,
  "requires_confirm": true,
  "allowed_actions": ["pr_edit"],
  "blocked_actions": ["pr_create", "push", "issue_comment", "merge"]
}
```

O método `can_worker_execute(workspace_id, worker_name, action, mode)` avalia cada restrição em cascata e bloqueia a ação caso:
- O módulo geral esteja desativado;
- O modo `background` esteja bloqueado globalmente;
- A UI tente chamar algo restrito a `cli`;
- A ação solicitada figure na lista de `blocked_actions` ou não conste na lista `allowed_actions`.

## Cockpit Integration

No Cockpit, adicionamos um bloco **read-only** no modal/painel de configuração do Workspace, demonstrando se os *External Workers* estão ligados e quais as permissões correntes. Uma mensagem instrutiva acompanha o painel, ressaltando a natureza offline por padrão do AIW.

> Workers externos continuam bloqueados por padrão. O Cockpit não executa GitHub/Jira, não roda daemon, não agenda jobs e não envia dados externos.

## Próximos Passos

Com a barreira consolidada, podemos com segurança evoluir o CLI de `aiw-integration-worker` para um daemon opcional (`aiw-worker-daemon`) que apenas consome intents e tenta aplicar ações **apenas se a Policy permitir**.

## Atualizações
A política agora está ativamente integrada ao *Integration Worker CLI*, bloqueando gh pr edit na origem se as diretrizes rejeitarem. Veja [AIW GitHub Worker Policy Integration](AIW_GITHUB_WORKER_POLICY_INTEGRATION.md).

O Foreground Worker Loop também consulta esta política ativamente via código antes de cada ciclo. Veja [AIW Foreground Worker Loop](AIW_FOREGROUND_WORKER_LOOP.md).
