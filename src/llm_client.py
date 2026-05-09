import os
import time
import requests
from dotenv import load_dotenv


class LLMClient:

    def __init__(self, host=None, model=None):
        load_dotenv()
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "gpt-oss:120b")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
        self.max_retries = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
        self.api_url = f"{self.host}/api/chat"

    def chat(self, prompt, system=None, temp=0.7, max_tokens=1024):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temp,
                "num_predict": max_tokens,
            },
        }

        last_error = None
        for tentativa in range(1, self.max_retries + 1):
            try:
                inicio = time.time()
                response = requests.post(self.api_url, json=payload, timeout=self.timeout)
                tempo_ms = round((time.time() - inicio) * 1000)
                response.raise_for_status()
                data = response.json()

                resposta_texto = data.get("message", {}).get("content", "").strip()
                tokens_prompt = data.get("prompt_eval_count", 0)
                tokens_resposta = data.get("eval_count", 0)

                return {
                    "resposta": resposta_texto,
                    "tokens_prompt": tokens_prompt,
                    "tokens_resposta": tokens_resposta,
                    "tempo_ms": tempo_ms,
                }

            except requests.exceptions.Timeout:
                last_error = f"Timeout apos {self.timeout}s (tentativa {tentativa}/{self.max_retries})"
                print(f"  AVISO: {last_error}")
            except requests.exceptions.ConnectionError:
                last_error = f"Erro de conexao com {self.host} (tentativa {tentativa}/{self.max_retries})"
                print(f"  AVISO: {last_error}")
            except requests.exceptions.HTTPError as e:
                last_error = f"Erro HTTP {e.response.status_code} (tentativa {tentativa}/{self.max_retries})"
                print(f"  AVISO: {last_error}")
            except Exception as e:
                last_error = f"Erro: {str(e)} (tentativa {tentativa}/{self.max_retries})"
                print(f"  AVISO: {last_error}")

            if tentativa < self.max_retries:
                wait_time = 2 ** tentativa
                print(f"  Aguardando {wait_time}s antes de tentar de novo...")
                time.sleep(wait_time)

        print(f"  FALHA apos {self.max_retries} tentativas: {last_error}")
        return {
            "resposta": f"[ERRO] {last_error}",
            "tokens_prompt": 0,
            "tokens_resposta": 0,
            "tempo_ms": 0,
        }

    def verificar_conexao(self):
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            modelos = [m["name"] for m in response.json().get("models", [])]
            print(f"  Ollama conectado em {self.host}")
            print(f"  Modelos disponiveis: {', '.join(modelos) if modelos else 'nenhum'}")
            return True
        except Exception as e:
            print(f"  Falha ao conectar com Ollama em {self.host}: {e}")
            return False
