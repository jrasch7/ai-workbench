# Project Context — SisOpERP Web

## Visão

SisOpERP Web é a evolução web do ERP legado da SisOp, originalmente baseado em Microsoft Access/VBA.

É um projeto real, ligado a empresas e operações existentes.

A prioridade é segurança, integridade dos dados, migração controlada e evolução gradual.

## Stack conhecida

- Next.js;
- TypeScript;
- Prisma;
- PostgreSQL;
- GitHub Actions;
- AWS staging;
- PM2/Next start em ambiente de staging;
- legado Access/VBA como fonte histórica importante.

## Contexto de negócio

SisOp atende empresas reais, incluindo fábricas e indústrias.

O legado em Access continua relevante e precisa ser respeitado durante migração, importação e rollback.

## Frentes importantes

- importação Access para Web;
- rollback/exportação Web para Access;
- atendimento e suporte técnico;
- CI/CD e AWS staging;
- multi-tenancy;
- permissões;
- módulos de pedidos, financeiro, caixa, estoque, fiscal, cadastros e usuários.

## Migração Access

O projeto possui documentação em docs/migracao_access.

A abordagem correta é diagnóstico, mapeamento, prova segura, dry-run, logs e só depois escrita limitada.

Pontos importantes:

- preservar IDs legados quando necessário;
- usar batch/import logs;
- evitar side effects sem dry-run;
- não rodar import destrutivo sem confirmação;
- mapear tabelas principais e auxiliares por prefixo.

## Rollback Web para Access

Objetivo futuro: gerar DB.accdb e estrutura de arquivos compatível para rollback emergencial.

Regras conhecidas:

- foco em DB.accdb;
- preservar dados críticos;
- fiscal deve priorizar XML autorizado;
- pedidos, caixa, financeiro, estoque, cadastros, produtos e contratos são críticos;
- dados sem equivalente no Access devem ir para relatório de não exportáveis;
- rotina final deve ser acionável pelo Web, não procedimento manual frágil.

## Atendimento técnico

Há decisão de evoluir a área de Atendimento com subfluxos internos como:

- SupportTicket;
- DevTask;
- AIAnalysis.

Esses dados não devem ser misturados com Attendance existente.

A implementação foi pausada até infraestrutura/ordem futura.

## Regras para agentes

Agente não deve:

- mexer em produção;
- alterar AWS staging sem autorização;
- rodar migrations reais sem permissão;
- inventar ownership entre João, Heron e Luciano;
- alterar fluxo legado sem diagnóstico;
- commitar/pushar sem validação e autorização.

Agente deve:

- trabalhar por branch ou worktree;
- respeitar PR pequeno;
- revisar git status e diff;
- validar com comandos do projeto;
- documentar decisões técnicas;
- separar executor, validator e integrator.

## Validação esperada

Depende da tarefa, mas pode incluir:

```text
npm run lint
npm run build
npx prisma validate
git diff --check
git status --short
```

Para tarefas de migração Access, validações devem ser específicas e preferencialmente dry-run.

## Uso no AI Workbench

Antes de qualquer tarefa real no SisOpERP Web, anexar este contexto e um task brief específico.

Nunca pedir ao agente para migrar tudo ou corrigir tudo de uma vez.

Tarefas devem ser pequenas, auditáveis e reversíveis.
