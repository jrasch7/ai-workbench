# AIW Coverage Run Capture

## Resultado

O Coverage Run Capture automatiza a integração da métrica de cobertura pós-teste dentro do Test Run History. Após a conclusão bem-sucedida de um test command, o runner faz um processamento best-effort (sem travar em erros) para ler e sumarizar os relatórios de coverage gerados.

## Thresholds

No workspace profile, você pode configurar um nível mínimo aceitável global ou por relatório:

```json
{
  "profile": {
    "coverage": {
      "default_threshold": 0.70,
      "changed_file_threshold": 0.70
    },
    "coverage_reports": [
      {
        "name": "Python coverage XML",
        "format": "cobertura_xml",
        "path": "coverage.xml",
        "threshold": 0.75
      }
    ]
  }
}
```

Limites: Entre 0 e 1.

## Captura após test-run

- Apenas captura no final de um command aprovado que gera arquivos no `resolved_path`.
- Não executa testes adicionais e nem injeta dependências extras no projeto.
- Status da extração se divide em `covered`, `partial`, `missing`, e `no_report`.

## Artifacts

O Runner cria os seguintes arquivos no diretório do teste `.aiw/workspaces/<workspace_id>/test-runs/<test_run_id>/`:
- `coverage-summary.json`
- `coverage-summary.md`

Além disso, adiciona metadados no `metadata.json` (`coverage_captured`, `coverage_status`, e `coverage_average_line_rate`).

## Integração com Patch Review Gate

O Review Gate agora prioriza relatórios de test-runs que estão ligados diretamente à validação do Patch atual. Caso o Snapshot capture a nova cobertura, a _source_ exibirá `test_run_capture`, agindo como a evidência definitiva da aprovação no check de Cobertura.

## Cockpit

- O detalhe visual de um **Test Run** aponta na lista o `Coverage capturado`.
- O payload de **Profile Validation** devolve logs com thresholds validados.
- O bloco visual **Coverage Report** do Review Gate indica a fonte dos dados capturados.

## Segurança

- Não instala dependências.
- Não executa coverage automaticamente (apenas executa test-commands validados do usuário que, idealmente, contêm o step apropriado).
- Só lê relatórios configurados.
- Paths relativos ao workspace, com checagens para não vazar a diretórios superiores.
- Sem shell livre, leitura via parser simples.
- Sem leitura de `.env`.

## Limitações

- Não gera relatório de coverage per se.
- Não mede as linhas exatas tocadas no diff (apenas mensura a aderência global dos changed-files no arquivo final).
- Não faz mutation testing.
- A captura ocorre de forma best-effort e silenciosa, sem bloquear a gravação do test-run se o report corromper.

## Próximo passo recomendado

Avaliar o suporte de captura nativa para frameworks frontend complexos e integração com Mutation Testing nos workflows assíncronos.

Integra com o [Coverage Baseline and Diff](AIW_COVERAGE_BASELINE_DIFF.md).
