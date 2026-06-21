# Backend do SafeGen

Serviço FastAPI responsável por:

- sanitização local via Ollama + `phi3:mini`;
- análise semântica externa via Gemini;
- exposição dos endpoints HTTP do fluxo híbrido.

Caminho de execução recomendado: rodar através da stack Docker na raiz do repositório.

## Avaliador do analisador semântico (Gemini)

Mede a qualidade da etapa de análise semântica, comparando a saída do Gemini com um dataset rotulado de prompts seguros/inseguros. Calcula precisão, recall, F1-score, taxa de falsos positivos e taxa de falsos negativos.

Pré-requisitos: Ollama rodando localmente com o modelo `phi3:mini` baixado, e a variável `GEMINI_API_KEY` configurada no `.env`.

Executar a partir da pasta `backend/`:

```
python avaliar_analisadores.py --dataset prompts_analise_semantica_gemini.json
```

Parâmetros opcionais:

- `--output-dir` — pasta onde salvar os relatórios (padrão: `./resultados`)
- `--delay` — espera entre chamadas, em segundos, para respeitar limite de taxa da API do Gemini
- `--limit` — avalia só os N primeiros prompts (útil para testes rápidos)
- `--no-sanitize` — pula a etapa do Phi-3 e envia o prompt original direto ao Gemini

Resultados gerados em `resultados/`: `resultados_detalhados.csv`, `metricas.json`, `falsos_positivos.json`, `falsos_negativos.json` e `erros_tecnicos.json`.