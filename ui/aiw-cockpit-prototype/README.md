# AIW Cockpit UI Prototype

## Objetivo
Este protótipo demonstra, de forma **isolada** e **navegável**, a nova interface do AIW Cockpit. Ele não possui backend, não altera nenhum código do Cockpit existente e serve apenas para visualização e validação de ideias de UI.

## Como abrir localmente
```bash
python3 -m http.server 8787 --directory ui/aiw-cockpit-prototype
```
Acesse `http://localhost:8787` no seu navegador.

## Escopo
- Apenas arquivos dentro de `ui/aiw-cockpit-prototype/` foram criados.
- Não toca nenhum código do Cockpit real, nem scripts existentes.
- Não há dependências nem `npm install`.

## Próximos passos para integração futura
- Conectar a APIs reais (LangGraph/LangChain) para alimentar os dados.
- Substituir fixtures por chamadas ao backend.
- Integrar com o fluxo de releases do AIW.

## Round 2 updates (alignment 5)
- Added Experiment Lab tab.
- Profile + Router selector UI in experiment page (reflects aiw/profiles + aiw/router).
- Providers page can show docker/devcontainer (via future data).
- Cockpit scripts updated to import from aiw.* for profiles/router/experiment/execution.
- Full alignment: consume only public aiw interfaces.

## Documentos do PR #7 que guiam a UI
- **Fundação AIW** – definições de dashboards e cards.
- **Interface principal** – estrutura de sidebar, header e badges.
- **Phase 7.6** – requisitos de Context Resilience e status CR‑0 a CR‑7.

Este protótipo permite navegar entre as telas:
- Dashboard
- Lista de Runs
- Detalhes de Run (Log, Diff, Handoff, Validator, Analysis)
- Agents / Providers mockados
- Context Resilience mockado
- Settings (placeholder)
