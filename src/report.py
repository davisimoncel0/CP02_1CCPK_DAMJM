import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
GRAFICOS_DIR = os.path.join(OUTPUT_DIR, "graficos")


def _garantir_diretorios():
    os.makedirs(os.path.abspath(GRAFICOS_DIR), exist_ok=True)


def gerar_tabela(resultados):
    _garantir_diretorios()
    df = pd.DataFrame(resultados)

    csv_path = os.path.join(os.path.abspath(OUTPUT_DIR), "resultados.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"\n  Resultados salvos em: {csv_path}")

    if not df.empty:
        resumo = df.groupby(["tarefa", "tecnica"]).agg(
            acuracia_media=("acuracia", "mean"),
            tokens_medio=("tokens_prompt", "mean"),
            tempo_medio_ms=("tempo_ms", "mean"),
        ).round(3)

        print("\n" + "=" * 70)
        print("  RESUMO COMPARATIVO POR TAREFA x TECNICA")
        print("=" * 70)
        print(resumo.to_string())
        print("=" * 70)

    return df


def grafico_acuracia(resultados):
    _garantir_diretorios()
    df = pd.DataFrame(resultados)

    if df.empty:
        print("  Sem dados para grafico de acuracia")
        return

    pivot = df.groupby(["tarefa", "tecnica"])["acuracia"].mean().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 6))
    pivot.plot(kind="bar", ax=ax, width=0.7, edgecolor="black", linewidth=0.5)

    ax.set_title("Acuracia Media por Tecnica de Prompting", fontsize=14, fontweight="bold")
    ax.set_xlabel("Tarefa", fontsize=11)
    ax.set_ylabel("Acuracia (0 a 1)", fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.legend(title="Tecnica", fontsize=9)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")

    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", fontsize=7, padding=2)

    plt.tight_layout()
    caminho = os.path.join(os.path.abspath(GRAFICOS_DIR), "acuracia_por_tecnica.png")
    fig.savefig(caminho, dpi=150)
    plt.close(fig)
    print(f"  Grafico de acuracia salvo em: {caminho}")


def grafico_custo(resultados):
    _garantir_diretorios()
    df = pd.DataFrame(resultados)

    if df.empty:
        print("  Sem dados para grafico de custo")
        return

    df["tokens_total"] = df["tokens_prompt"] + df["tokens_resposta"]
    custo = df.groupby("tecnica")[["tokens_prompt", "tokens_resposta"]].mean()

    fig, ax = plt.subplots(figsize=(10, 6))
    custo.plot(kind="bar", stacked=True, ax=ax, edgecolor="black", linewidth=0.5,
               color=["#3498db", "#e74c3c"])

    ax.set_title("Custo Medio em Tokens por Tecnica", fontsize=14, fontweight="bold")
    ax.set_xlabel("Tecnica", fontsize=11)
    ax.set_ylabel("Tokens Medios", fontsize=11)
    ax.legend(["Tokens Prompt", "Tokens Resposta"], fontsize=9)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")

    plt.tight_layout()
    caminho = os.path.join(os.path.abspath(GRAFICOS_DIR), "custo_tokens_por_tecnica.png")
    fig.savefig(caminho, dpi=150)
    plt.close(fig)
    print(f"  Grafico de custo salvo em: {caminho}")


def grafico_temperatura(resultados_temp):
    _garantir_diretorios()

    if not resultados_temp:
        print("  Sem dados para grafico de temperatura")
        return

    temps = [r["temperatura"] for r in resultados_temp]
    consistencias = [r["consistencia"] for r in resultados_temp]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        [str(t) for t in temps], consistencias,
        color=["#2ecc71", "#f39c12", "#e74c3c"],
        edgecolor="black", linewidth=0.5,
    )

    ax.set_title("Consistencia por Temperatura", fontsize=14, fontweight="bold")
    ax.set_xlabel("Temperatura", fontsize=11)
    ax.set_ylabel("Consistencia (0 a 1)", fontsize=11)
    ax.set_ylim(0, 1.1)

    for bar, val in zip(bars, consistencias):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{val:.2f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    caminho = os.path.join(os.path.abspath(GRAFICOS_DIR), "consistencia_temperatura.png")
    fig.savefig(caminho, dpi=150)
    plt.close(fig)
    print(f"  Grafico de temperatura salvo em: {caminho}")


def recomendar(resultados):
    df = pd.DataFrame(resultados)
    if df.empty:
        return {}

    recomendacoes = {}
    tarefas = df["tarefa"].unique()

    print("\n" + "=" * 70)
    print("  RECOMENDACAO - MELHOR TECNICA POR TAREFA")
    print("=" * 70)

    for tarefa in tarefas:
        df_tarefa = df[df["tarefa"] == tarefa]
        resumo = df_tarefa.groupby("tecnica").agg(
            acuracia_media=("acuracia", "mean"),
            tokens_medio=("tokens_prompt", "mean"),
        ).round(3)

        resumo_sorted = resumo.sort_values(
            by=["acuracia_media", "tokens_medio"],
            ascending=[False, True],
        )
        melhor = resumo_sorted.index[0]
        melhor_dados = resumo_sorted.iloc[0]

        justificativa = (
            f"A tecnica '{melhor}' obteve a melhor acuracia media "
            f"({melhor_dados['acuracia_media']:.1%}) para a tarefa '{tarefa}', "
            f"com custo medio de {melhor_dados['tokens_medio']:.0f} tokens."
        )

        recomendacoes[tarefa] = {
            "melhor_tecnica": melhor,
            "acuracia_media": float(melhor_dados["acuracia_media"]),
            "tokens_medio": float(melhor_dados["tokens_medio"]),
            "justificativa": justificativa,
        }

        print(f"\n  Tarefa: {tarefa}")
        print(f"  Melhor tecnica: {melhor}")
        print(f"  Acuracia media: {melhor_dados['acuracia_media']:.1%}")
        print(f"  Tokens medio: {melhor_dados['tokens_medio']:.0f}")
        print(f"  {justificativa}")

    print("\n" + "=" * 70)
    return recomendacoes
