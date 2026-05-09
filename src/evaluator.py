import json
import re
import tiktoken


def contar_tokens(texto, encoding_name="cl100k_base"):
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(texto))
    except Exception:
        return len(texto.split()) * 2


def normalizar_texto(texto):
    texto = texto.strip().lower()
    texto = re.sub(r'["\'\.\,\!\?\;\:\-\_\(\)\[\]\{\}]', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def medir_acuracia(resposta, esperado, tipo_tarefa="classificacao"):
    if not resposta or resposta.startswith("[ERRO]"):
        return 0.0

    if tipo_tarefa == "classificacao":
        return _acuracia_classificacao(resposta, esperado)
    elif tipo_tarefa == "extracao":
        return _acuracia_extracao(resposta, esperado)
    elif tipo_tarefa == "sumarizacao":
        return _acuracia_sumarizacao(resposta, esperado)
    else:
        return _acuracia_classificacao(resposta, esperado)


def _acuracia_classificacao(resposta, esperado):
    resp_norm = normalizar_texto(resposta)
    esp_norm = normalizar_texto(str(esperado))

    if resp_norm == esp_norm:
        return 1.0
    if esp_norm in resp_norm:
        return 0.8
    return 0.0


def _acuracia_extracao(resposta, esperado):
    if isinstance(esperado, str):
        try:
            esperado = json.loads(esperado)
        except json.JSONDecodeError:
            return _acuracia_classificacao(resposta, esperado)

    try:
        json_match = re.search(r'\{[^{}]*\}', resposta, re.DOTALL)
        if json_match:
            resp_json = json.loads(json_match.group())
        else:
            return 0.0
    except (json.JSONDecodeError, AttributeError):
        return 0.0

    if not isinstance(esperado, dict):
        return 0.0

    campos_total = len(esperado)
    campos_corretos = 0

    for chave, valor_esp in esperado.items():
        valor_resp = resp_json.get(chave, None)
        if valor_resp is not None and valor_esp is not None:
            if normalizar_texto(str(valor_resp)) == normalizar_texto(str(valor_esp)):
                campos_corretos += 1
            elif normalizar_texto(str(valor_esp)) in normalizar_texto(str(valor_resp)):
                campos_corretos += 0.5

    return campos_corretos / campos_total if campos_total > 0 else 0.0


def _acuracia_sumarizacao(resposta, esperado):
    resp_norm = normalizar_texto(resposta)
    esp_norm = normalizar_texto(str(esperado))

    keywords = [p for p in esp_norm.split() if len(p) >= 4]
    if not keywords:
        return 0.5

    encontradas = sum(1 for kw in keywords if kw in resp_norm)
    return min(1.0, encontradas / len(keywords))


def medir_consistencia(respostas):
    if not respostas:
        return 0.0

    normalizadas = [normalizar_texto(r) for r in respostas]
    mais_comum = max(set(normalizadas), key=normalizadas.count)
    return normalizadas.count(mais_comum) / len(normalizadas)


def testar_temperatura(llm_client, prompt, system=None, temps=None, repeticoes=3):
    if temps is None:
        temps = [0.1, 0.5, 1.0]

    resultados = []
    for temp in temps:
        respostas = []
        for _ in range(repeticoes):
            resultado = llm_client.chat(prompt, system=system, temp=temp)
            respostas.append(resultado["resposta"])

        consistencia = medir_consistencia(respostas)
        resultados.append({
            "temperatura": temp,
            "respostas": respostas,
            "consistencia": consistencia,
        })

    return resultados
