# SDK de Agentes Fluaai

SDK em Python para interagir com a API de Agentes da Fluaai, oferecendo integração simples com LLMs e operadores, suporte a streaming, e respostas estruturadas em classes tipadas.

## Instalação

```bash
pip install fluaaiagentsdk
```

## Funcionalidades

- Invocação de agentes LLM e Operador
- Streaming em tempo real de respostas
- Tratamento consistente de diferentes engines
- Respostas tipadas com classes ou compatíveis com JSON
- Suporte a ferramentas e processamento de conversas

### Streaming em Tempo Real

```python
import asyncio
from fluaaiagentsdk import Agent, Channels

async def main():
    # Receber resposta em tempo real via streaming
    async for chunk in await Agent.agent_invoke(
        prompt="Gere uma imagem de montanhas",
        agent_id="seu_agent_id",
        api_key="sua_chave_api_key",
        dynamic_variables={"client_name": "Gabriel"},
        channel=Channels.integration
    ):
        # Acessar como objeto
        print(chunk.output, end="", flush=True)
        
        # Para agentes Operador, verificar status
        if chunk.engine == "operator" and chunk.status:
            if chunk.status == "finished":
                print(f"\n[Tarefa concluída]")
                print(f"URL ao vivo: {chunk.live_url}")
                print(f"URL's das ações: {chunk.screenshots}")

asyncio.run(main())
```

## Estrutura de Respostas

O SDK retorna respostas como objetos estruturados da classe `AgentResponse`:

### Classe AgentResponse

**Atributos principais:**
- `engine`: Engine do agente ("llm" ou "operator")
- `conversation_id`: ID da conversa
- `output`: Conteúdo da resposta

**Atributos para engine operator:**
- `task_id`: ID da tarefa do operador
- `live_url`: URL para visualizar a execução em tempo real
- `status`: Status da tarefa ("created", "running", "finished", "stopped", "paused", "failed")
- `screenshots`: Lista de URLs de screenshots das ações

**Métodos:**
- `to_dict()`: Converte para dicionário Python
- `to_json()`: Converte para string JSON
- `from_dict(data)`: Cria objeto a partir de dicionário
- `from_json(json_str)`: Cria objeto a partir de JSON

## Formatos de Resposta por Engine

### 1. Engine 'llm' (LLM tradicional)

```python
AgentResponse(
    engine="llm",
    output="Conteúdo completo da resposta do modelo de linguagem...",
)
```

### 2. Engine 'operator' (Operador)

```python
AgentResponse(
    engine="operator",
    output="Resultado completo da tarefa do operador...",
    task_id="661d49e4-aada-4d90-abc7-baba34a7b762",
    live_url="https://live.anchorbrowser.io?sessionId=98e2dd75-33d6-44ab-9e4f-9298e8817cc5",
    status="finished",
    screenshots=[...]  # URLs de screenshots
)
```