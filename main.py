import sys
from dotenv import load_dotenv

from src.llm_client import LLMClient
from src.tasks import TAREFAS, carregar_inputs, carregar_exemplos, carregar_personas
from src.techniques import zero_shot, few_shot, chain_of_thought, role_prompting
from src.evaluator import contar_tokens, medir_acuracia, testar_temperatura
from src.report import gerar_tabela, grafico_acuracia, grafico_custo, grafico_temperatura, recomendar


TECNICAS = ["zero_shot", "few_shot", "chain_of_thought", "role_prompting"]


def executar_tecnica(tecnica_nome, tarefa, input_dados, exemplos, personas, llm):
    if tecnica_nome == "zero_shot":
        prompt = zero_shot(tarefa, input_dados)
        return llm.chat(prompt), prompt, None

    elif tecnica_nome == "few_shot":
        prompt = few_shot(tarefa, input_dados, exemplos)
        return llm.chat(prompt), prompt, None

    elif tecnica_nome == "chain_of_thought":
        prompt = chain_of_thought(tarefa, input_dados, tarefa["passos_cot"])
        return llm.chat(prompt), prompt, None

    elif tecnica_nome == "role_prompting":
        persona_key = tarefa.get("persona", "analista_cx")
        persona = personas.get(persona_key, {})
        system_prompt, user_prompt = role_prompting(tarefa, input_dados, persona)
        return llm.chat(user_prompt, system=system_prompt), user_prompt, system_prompt

    return None, None, None


def main():
    load_dotenv()

    print("=" * 70)
    print("  PROMPT TOOLKIT - Comparador de Tecnicas de Prompting")
    print("  Dominio: E-commerce / Atendimento ao Cliente")
    print("=" * 70)

    # 1. conectar no ollama
    print("\nConectando ao Ollama...")
    llm = LLMClient()

    if not llm.verificar_conexao():
        print("\nNao foi possivel conectar ao Ollama.")
        print("Certifique-se de que o Ollama esta rodando:")
        print("  $ ollama serve")
        print(f"  $ ollama pull {llm.model}")
        sys.exit(1)

    # 2. carregar personas
    print("\nCarregando personas...")
    personas = carregar_personas()
    print(f"  Personas: {', '.join(personas.keys())}")

    # 3. rodar todas as tarefas
    todos_resultados = []
    melhores_prompts = {}

    for tarefa in TAREFAS:
        nome_tarefa = tarefa["nome"]
        tipo_tarefa = tarefa["tipo"]

        print(f"\n{'─' * 70}")
        print(f"  Tarefa: {nome_tarefa} (tipo: {tipo_tarefa})")
        print(f"{'─' * 70}")

        inputs = carregar_inputs(nome_tarefa)
        exemplos = carregar_exemplos(nome_tarefa)

        if not inputs:
            print(f"  Nenhum input encontrado para '{nome_tarefa}'. Pulando...")
            continue

        print(f"  {len(inputs)} inputs carregados")
        print(f"  {len(exemplos)} exemplos few-shot carregados")

        melhor_acuracia = -1
        melhor_tecnica_info = None

        for tecnica in TECNICAS:
            print(f"\n  Tecnica: {tecnica}")
            acuracias_tecnica = []

            for i, item in enumerate(inputs):
                input_texto = item["input"]
                esperado = item["esperado"]

                print(f"    Input {i+1}/{len(inputs)}: {input_texto[:50]}...")

                resultado_llm, prompt_usado, system_usado = executar_tecnica(
                    tecnica, tarefa, input_texto, exemplos, personas, llm
                )

                if resultado_llm is None:
                    continue

                acuracia = medir_acuracia(resultado_llm["resposta"], esperado, tipo_tarefa)
                acuracias_tecnica.append(acuracia)

                todos_resultados.append({
                    "tarefa": nome_tarefa,
                    "tipo": tipo_tarefa,
                    "tecnica": tecnica,
                    "input_texto": input_texto[:100],
                    "resposta": resultado_llm["resposta"][:200],
                    "esperado": str(esperado)[:200],
                    "acuracia": acuracia,
                    "tokens_prompt": resultado_llm["tokens_prompt"],
                    "tokens_resposta": resultado_llm["tokens_resposta"],
                    "tempo_ms": resultado_llm["tempo_ms"],
                })

                print(f"      Acuracia: {acuracia:.2f} | "
                      f"Tokens: {resultado_llm['tokens_prompt']}+{resultado_llm['tokens_resposta']} | "
                      f"Tempo: {resultado_llm['tempo_ms']}ms")

            if acuracias_tecnica:
                media = sum(acuracias_tecnica) / len(acuracias_tecnica)
                print(f"    Acuracia media ({tecnica}): {media:.2%}")

                if media > melhor_acuracia:
                    melhor_acuracia = media
                    melhor_tecnica_info = {
                        "tecnica": tecnica,
                        "prompt": prompt_usado,
                        "system": system_usado,
                    }

        if melhor_tecnica_info:
            melhores_prompts[nome_tarefa] = melhor_tecnica_info

    # 4. gerar relatorio
    print("\n\nGERANDO RELATORIO...")
    print("=" * 70)

    if not todos_resultados:
        print("  Nenhum resultado para gerar relatorio.")
        sys.exit(0)

    df = gerar_tabela(todos_resultados)
    grafico_acuracia(todos_resultados)
    grafico_custo(todos_resultados)
    recomendacoes = recomendar(todos_resultados)

    # 5. teste de temperatura no melhor prompt
    print("\n\nTESTE DE TEMPERATURA")
    print("=" * 70)

    for nome_tarefa, info in melhores_prompts.items():
        print(f"\n  Tarefa: {nome_tarefa}")
        print(f"  Melhor tecnica: {info['tecnica']}")
        print(f"  Testando temperaturas: 0.1, 0.5, 1.0 (3 repeticoes cada)...")

        resultados_temp = testar_temperatura(
            llm,
            prompt=info["prompt"],
            system=info.get("system"),
            temps=[0.1, 0.5, 1.0],
            repeticoes=3,
        )

        for r in resultados_temp:
            print(f"    Temp {r['temperatura']}: consistencia = {r['consistencia']:.2%}")

        grafico_temperatura(resultados_temp)

    # 6. fim
    print("\n\n" + "=" * 70)
    print("  TOOLKIT CONCLUIDO")
    print("  Resultados em: output/")
    print("  CSV: output/resultados.csv")
    print("  Graficos: output/graficos/")
    print("=" * 70)


if __name__ == "__main__":
    main()
