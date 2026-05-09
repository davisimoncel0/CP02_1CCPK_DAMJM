# PromptToolkit

Checkpoint 02 - FIAP - Prompt Engineering & AI

Toolkit Python que aplica 4 tecnicas de prompting (Zero-Shot, Few-Shot, Chain-of-Thought e Role Prompting) a tarefas de e-commerce, compara os resultados e recomenda a melhor abordagem.

## Dominio

E-commerce / Atendimento ao Cliente. O toolkit avalia 3 tarefas:

- **Classificacao de Sentimento** - classifica reviews como POSITIVO/NEGATIVO/NEUTRO/MISTO
- **Extracao de Dados de Pedido** - extrai produto, preco, problema e numero do pedido
- **Sumarizacao de Reviews** - resume reviews longas em 2-3 frases

## Stack

- Python 3.10+
- Ollama API (local/gratuito) com modelo `gpt-oss:120b`
- tiktoken para contagem de tokens
- matplotlib + pandas para graficos e tabelas

## Como instalar

1. Clonar o repositorio:
```bash
git clone <URL_DO_REPOSITORIO>
cd prompt-toolkit
```

2. Criar ambiente virtual (opcional):
```bash
python -m venv venv
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar o .env:
```bash
cp .env.example .env
```

5. Iniciar o Ollama e baixar o modelo:
```bash
ollama serve
ollama pull gpt-oss:120b
```

## Como executar

```bash
python main.py
```

O toolkit vai:
1. Conectar no Ollama
2. Rodar cada tarefa com as 4 tecnicas
3. Avaliar acuracia e custo de cada uma
4. Gerar tabela CSV e graficos em `output/`
5. Recomendar a melhor tecnica por tarefa
6. Testar temperaturas (0.1, 0.5, 1.0) no melhor prompt

## Estrutura do projeto

```
prompt-toolkit/
├── README.md
├── requirements.txt
├── .env.example
├── main.py
├── src/
│   ├── __init__.py
│   ├── llm_client.py          # conexao com Ollama
│   ├── prompt_builder.py      # montagem dos prompts
│   ├── techniques.py          # 4 tecnicas de prompting
│   ├── tasks.py               # definicao das tarefas
│   ├── evaluator.py           # metricas de avaliacao
│   └── report.py              # graficos e tabelas
├── data/
│   ├── inputs.json            # inputs reais por tarefa
│   └── examples.json          # exemplos para few-shot
├── prompts/
│   ├── system_prompts.json    # personas para role prompting
│   └── templates.json         # templates de prompt
├── output/
│   ├── resultados.csv
│   └── graficos/
└── docs/
    └── CP02_NomeDoGrupo.pdf
```

## Tecnicas de Prompting

- **Zero-Shot**: prompt direto, sem exemplos
- **Few-Shot**: prompt com 2-3 exemplos demonstrativos
- **Chain-of-Thought**: raciocinio passo a passo antes da resposta
- **Role Prompting**: persona especialista no system prompt

## Grupo

Curso: Prompt Engineering & AI - FIAP 2026
