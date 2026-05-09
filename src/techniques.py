from src.prompt_builder import montar_prompt, adicionar_exemplos, adicionar_cot


def zero_shot(tarefa, input_dados):
    prompt = montar_prompt(
        instrucao=tarefa["instrucao"],
        contexto=tarefa.get("contexto", "Analise o texto fornecido."),
        input_dados=input_dados,
        formato_output=tarefa["formato_output"],
    )
    return prompt


def few_shot(tarefa, input_dados, exemplos):
    prompt = montar_prompt(
        instrucao=tarefa["instrucao"],
        contexto=tarefa.get("contexto", "Analise o texto fornecido."),
        input_dados=input_dados,
        formato_output=tarefa["formato_output"],
    )
    prompt = adicionar_exemplos(prompt, exemplos)
    return prompt


def chain_of_thought(tarefa, input_dados, passos):
    prompt = montar_prompt(
        instrucao=tarefa["instrucao"],
        contexto=tarefa.get("contexto", "Analise o texto fornecido."),
        input_dados=input_dados,
        formato_output=tarefa["formato_output"],
    )
    prompt = adicionar_cot(prompt, passos)
    return prompt


def role_prompting(tarefa, input_dados, persona):
    system_prompt = persona.get("system_prompt", "Voce e um assistente util.")

    user_prompt = montar_prompt(
        instrucao=tarefa["instrucao"],
        contexto=tarefa.get("contexto", "Analise o texto fornecido."),
        input_dados=input_dados,
        formato_output=tarefa["formato_output"],
    )

    return (system_prompt, user_prompt)
