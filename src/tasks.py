import json
import os


TAREFAS = [
    {
        "nome": "classificacao_sentimento",
        "tipo": "classificacao",
        "instrucao": "Classifique o sentimento da review do cliente como POSITIVO, NEGATIVO, NEUTRO ou MISTO.",
        "contexto": "Voce esta analisando reviews de clientes de um e-commerce brasileiro.",
        "formato_output": "Responda APENAS com uma unica palavra: POSITIVO, NEGATIVO, NEUTRO ou MISTO.",
        "exemplos_fewshot": [
            {"input": "Adorei o produto, superou todas as expectativas!", "output": "POSITIVO"},
            {"input": "Pessimo atendimento, produto veio quebrado.", "output": "NEGATIVO"},
            {"input": "Bom preco, mas a qualidade deixa a desejar.", "output": "MISTO"},
        ],
        "passos_cot": [
            "Identifique palavras e expressoes de sentimento",
            "Liste os aspectos positivos mencionados",
            "Liste os aspectos negativos mencionados",
            "Compare a intensidade positivo vs negativo",
            "Classifique como POSITIVO, NEGATIVO, NEUTRO ou MISTO",
        ],
        "persona": "analista_cx",
    },
    {
        "nome": "extracao_dados_pedido",
        "tipo": "extracao",
        "instrucao": "Extraia as informacoes estruturadas da reclamacao do cliente.",
        "contexto": "Voce esta processando reclamacoes de clientes de um e-commerce.",
        "formato_output": "Responda APENAS com JSON: {\"produto\", \"preco\", \"problema\", \"pedido\"}. Use null se ausente.",
        "exemplos_fewshot": [
            {
                "input": "Meu Monitor LG Ultrawide de R$2.100,00 veio riscado. Pedido #55123.",
                "output": "{\"produto\": \"Monitor LG Ultrawide\", \"preco\": \"R$2.100,00\", \"problema\": \"tela riscada\", \"pedido\": \"#55123\"}",
            },
            {
                "input": "O Teclado Redragon de R$350,00 tem teclas ruins. Pedido #67890.",
                "output": "{\"produto\": \"Teclado Redragon\", \"preco\": \"R$350,00\", \"problema\": \"teclas que nao respondem\", \"pedido\": \"#67890\"}",
            },
        ],
        "passos_cot": [
            "Identifique o nome do produto",
            "Encontre o valor/preco (R$X.XXX,XX)",
            "Identifique o problema ou defeito",
            "Encontre o numero do pedido (#XXXXX)",
            "Monte o JSON com os campos extraidos",
        ],
        "persona": "especialista_dados",
    },
    {
        "nome": "sumarizacao_review",
        "tipo": "sumarizacao",
        "instrucao": "Crie um resumo executivo conciso da review detalhada do produto.",
        "contexto": "Voce esta processando reviews detalhadas para o time de produto.",
        "formato_output": "Resumo de 2-3 frases: pontos positivos, negativos e custo-beneficio.",
        "exemplos_fewshot": [
            {
                "input": "Mochila notebook 15\". Material impermeavel, varios compartimentos, alcas confortaveis. Ziper travou apos 1 mes, bolso lateral pequeno. R$189.",
                "output": "Mochila resistente com bons compartimentos e conforto. Ziper fragil e bolso lateral pequeno. Adequada para trabalho por R$189.",
            },
            {
                "input": "Mouse gamer 16000 DPI. Precisao incrivel, ergonomico, botoes programaveis. RGB bonita mas software instavel. Cabo rigido. R$250.",
                "output": "Mouse gamer preciso e ergonomico com botoes programaveis. Software instavel e cabo rigido. Bom custo-beneficio por R$250.",
            },
        ],
        "passos_cot": [
            "Identifique o produto e caracteristicas principais",
            "Liste os pontos positivos",
            "Liste os pontos negativos",
            "Identifique preco e custo-beneficio",
            "Sintetize em resumo de 2-3 frases",
        ],
        "persona": "analista_cx",
    },
]


def carregar_inputs(nome_tarefa):
    caminho = os.path.join(os.path.dirname(__file__), "..", "data", "inputs.json")
    with open(os.path.abspath(caminho), "r", encoding="utf-8") as f:
        return json.load(f).get(nome_tarefa, [])


def carregar_exemplos(nome_tarefa):
    caminho = os.path.join(os.path.dirname(__file__), "..", "data", "examples.json")
    with open(os.path.abspath(caminho), "r", encoding="utf-8") as f:
        return json.load(f).get(nome_tarefa, [])


def carregar_personas():
    caminho = os.path.join(os.path.dirname(__file__), "..", "prompts", "system_prompts.json")
    with open(os.path.abspath(caminho), "r", encoding="utf-8") as f:
        return json.load(f)


def obter_tarefa(nome):
    for tarefa in TAREFAS:
        if tarefa["nome"] == nome:
            return tarefa
    return None
