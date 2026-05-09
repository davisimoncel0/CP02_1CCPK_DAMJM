import json


def montar_prompt(instrucao, contexto, input_dados, formato_output):
    # valida que nada ta vazio
    if not instrucao or not instrucao.strip():
        raise ValueError("instrucao nao pode estar vazia")
    if not contexto or not contexto.strip():
        raise ValueError("contexto nao pode estar vazio")
    if not input_dados or not input_dados.strip():
        raise ValueError("input_dados nao pode estar vazio")
    if not formato_output or not formato_output.strip():
        raise ValueError("formato_output nao pode estar vazio")

    prompt = (
        f"### Instrucao\n{instrucao.strip()}\n\n"
        f"### Contexto\n{contexto.strip()}\n\n"
        f"### Dados de Entrada\n{input_dados.strip()}\n\n"
        f"### Formato de Saida\n{formato_output.strip()}"
    )
    return prompt


def adicionar_exemplos(prompt, exemplos):
    if not exemplos:
        return prompt

    exemplos_texto = "### Exemplos\n"
    for i, exemplo in enumerate(exemplos, 1):
        input_ex = exemplo.get("input", "")
        output_ex = exemplo.get("output", "")
        if isinstance(output_ex, dict):
            output_ex = json.dumps(output_ex, ensure_ascii=False, indent=2)

        exemplos_texto += f"\n**Exemplo {i}:**\n"
        exemplos_texto += f"Input: \"{input_ex}\"\n"
        exemplos_texto += f"Output: {output_ex}\n"

    if "### Dados de Entrada" in prompt:
        partes = prompt.split("### Dados de Entrada")
        prompt = partes[0] + exemplos_texto + "\n### Dados de Entrada" + partes[1]
    else:
        prompt = prompt + "\n\n" + exemplos_texto

    return prompt


def adicionar_cot(prompt, passos):
    if not passos:
        return prompt

    cot_texto = "### Raciocinio Passo a Passo\n"
    cot_texto += "Antes de dar sua resposta final, siga estes passos:\n\n"
    for i, passo in enumerate(passos, 1):
        cot_texto += f"{i}. {passo}\n"
    cot_texto += "\nApos seguir todos os passos, forneca sua resposta final.\n"

    if "### Dados de Entrada" in prompt:
        partes = prompt.split("### Dados de Entrada")
        prompt = partes[0] + cot_texto + "\n### Dados de Entrada" + partes[1]
    else:
        prompt = prompt + "\n\n" + cot_texto

    return prompt
