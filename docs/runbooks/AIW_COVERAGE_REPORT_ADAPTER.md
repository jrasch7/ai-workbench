# AIW Coverage Report Adapter

## Resultado

O Coverage Report Adapter processa e extrai informações de arquivos de cobertura já existentes gerados por comandos de testes. Ao contrário da intenção heurística de cobertura, esta funcionalidade lê diretamente relatórios LCOV e Cobertura XML para comprovar, de forma real, qual a proporção de linhas modificadas que de fato possui testes, e atribui um "Line-rate" por arquivo para uso do Patch Review Gate.

## coverage_reports

O bloco `coverage_reports` é uma funcionalidade opcional no profile do workspace:
```json
{
  "profile": {
    "coverage_reports": [
      {
        "name": "Python coverage XML",
        "format": "cobertura_xml",
        "path": "coverage.xml"
      }
    ]
  }
}
```

## Formatos suportados

- Cobertura XML / coverage.py XML
- LCOV

## Integração com Patch Review Gate

O Patch Review Gate cruza os dados do relatório com os `changed_files` do patch para decidir a integridade de cobertura da submissão:
- **Status covered**: Dá bônus de +5 pontos.
- **Status partial**: Retorna warning (com penalidade de -5).
- **Status missing**: Retorna warning se o relatório existe e não há cobertura para os arquivos alterados (penalidade de -10).
- **Status no_report**: Não altera pontuação (info) e funciona como aviso.
- **Status unknown**: Aviso informativo caso o parse falhe ou existam dados insuficientes.

O Review Gate não bloqueia patches por falta de cobertura total, atuando apenas sobre os scores de "Readiness". Continua trabalhando em paralelo com o "Test Coverage Intent" heurístico.

## Segurança

- Não instala dependências.
- Não executa coverage automaticamente, cabendo ao Validation Plan providenciar os relatórios nas etapas de teste se desejado.
- Não lê `.env` e impõe validação estrita nos arquivos para garantir segurança do sistema (apenas permitidos caminhos seguros contidos no repositório).
- Paths relativos ao workspace (bloqueado caminho absoluto e caminhos ascendentes `..`).
- Sem _shell livre_. A validação baseia-se unicamente em parsers XML e strings da biblioteca padrão.

## Limitações

- Threshold fixo: A v1 exige `70%` de média mínima em cobertura das modificações reportadas.
- Parsing simples: Ignora branching, complexity e métricas granulares em favor de cobertura por linha simples (Line-rate).
- Não mede linhas exatas do diff ainda, o Line-rate refere-se à cobertura global do arquivo modificado.
- Sem _mutation testing_: Incapaz de atestar se o teste passa verificações substanciais.
- Sem geração automática de relatórios.

## Próximo passo recomendado

Permitir configuração dinâmica de _threshold_ por `workspace_profile` e avaliar a adição de Mutation Testing para robustez avançada de testes automatizados com IA, bloqueando fixamente applies onde linhas vitais introduzidas ficaram orfãs.

Veja também a captura por [Coverage Run Capture](AIW_COVERAGE_RUN_CAPTURE.md).
