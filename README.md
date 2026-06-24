# Backend do SafeGen

Serviço FastAPI responsável por:

- sanitização local via Ollama + `phi3:mini`;
- análise semântica externa via Gemini;
- exposição dos endpoints HTTP do fluxo híbrido.

Caminho de execução recomendado: rodar através da stack Docker na raiz do repositório.

## Avaliação dos analisadores

O avaliador foi separado entre `semantic_analysis` e `local_analysis`.

### `semantic_analysis`

Mede a qualidade da etapa semântica comparando o campo `security_risk` retornado pelo Gemini com o valor de referência do arquivo `prompts_analise_semantica_gemini.json`. Nesta avaliação, cada item usa diretamente o seu `prompt` original.

Pré-requisitos: variáveis `GEMINI_API_KEY1` até `GEMINI_API_KEY6` configuradas no `.env` conforme disponibilidade das chaves.

Executar a partir da pasta `backend/`:

```bash
python avaliar_analisadores.py semantic_analysis
```

Parâmetros opcionais:

- `--dataset` — caminho do dataset JSON (padrão: `prompts_analise_semantica_gemini.json`)
- `--output-dir` — pasta onde salvar os relatórios (padrão: `./resultados/semantic_analysis`)
- `--limit` — avalia só os N primeiros prompts

O cliente do Gemini agora alterna entre `GEMINI_API_KEY1` até `GEMINI_API_KEY6`, respeitando no código o limite de `5 RPM` e `20 RPD` por chave e fazendo retentativa automática em falhas transitórias como `503`.

### `local_analysis`

Mede a qualidade da etapa local comparando o campo `sensitive_data` retornado pelo Phi-3/Ollama com o valor de referência do arquivo `prompts_analise_local_phi3.json`.

Pré-requisitos: Ollama rodando localmente com o modelo `phi3:mini` disponível.

Executar a partir da pasta `backend/`:

```bash
python avaliar_analisadores.py local_analysis
```

Parâmetros opcionais:

- `--dataset` — caminho do dataset JSON (padrão: `prompts_analise_local_phi3.json`)
- `--output-dir` — pasta onde salvar os relatórios (padrão: `./resultados/local_analysis`)
- `--limit` — avalia só os N primeiros prompts
