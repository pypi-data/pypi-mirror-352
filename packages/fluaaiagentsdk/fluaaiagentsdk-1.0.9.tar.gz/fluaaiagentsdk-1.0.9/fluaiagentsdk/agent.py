import json
import logging
import aiohttp
from enum import Enum
from dataclasses import dataclass
from dataclasses import dataclass, field, asdict
from typing import Tuple, Dict, AsyncGenerator, Union, Optional, List, Any

logger = logging.getLogger(__name__)

class AgentEngine(Enum):
    operator = "operator"
    llm = "llm"

class Channels(Enum):
    """Canais para gerenciamento de conversas."""
    integration = "integration"
    whatsapp = "whatsapp"

@dataclass
class AgentResponse:
    """Representa a resposta de um agente."""
    engine: str = ""
    conversation_id: str = ""
    output: str = ""
    
    # Campos específicos para engine 'operator'
    task_id: Optional[str] = None
    live_url: Optional[str] = None
    status: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a resposta para um dicionário."""
        result = asdict(self)
        return result
    
    def to_json(self) -> str:
        """Converte a resposta para uma string JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentResponse':
        """Cria uma instância de AgentResponse a partir de um dicionário."""
        response = cls(
            engine=data.get('engine', ''),
            conversation_id=data.get('conversation_id', ''),
            output=data.get('output', ''),
            task_id=data.get('task_id', None),
            live_url=data.get('live_url', None),
            status=data.get('status', None),
            screenshots=data.get('screenshots', None),
        )

        response.__post_init__()
        
        return response
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentResponse':
        """Cria uma instância de AgentResponse a partir de uma string JSON."""
        return cls.from_dict(json.loads(json_str))
    
    def __getitem__(self, key: str) -> Any:
        """
        Permite acessar campos como se fosse um dicionário para compatibilidade
        com código existente. Por exemplo: response['output']
        """
        if hasattr(self, key):
            return getattr(self, key)
        
        # Levantar KeyError para comportamento consistente com dicionários
        raise KeyError(f"'{key}' não encontrado em AgentResponse")

class Agent:
    CHAT_STREAM_API_URL = "https://chat-stream-api.azurewebsites.net/chat"
    
    @staticmethod
    async def agent_invoke(
        prompt: str,
        api_key: str = None,
        agent_id: str = None,
        conversation_id: str = None,
        channel: Channels = Channels.integration,
        dynamic_variables: Optional[Dict[str, Any]] = None,
        debug: Optional[bool] = False
    ) -> Union[Tuple[bool, Dict], AsyncGenerator[Tuple[bool, Dict], None]]:
        """
        Invoca um agente com opções de streaming flexíveis e autenticação.
        
        Args:
            prompt: Texto enviado ao agente
            api_key: Chave de API para autenticação (opcional)
            agent_id: ID do agente
            conversation_id: ID da conversa (opcional, gera um novo se não fornecido)
            stream_mode: Modo de streaming (DISABLED, ENABLED)
            on_chunk: Callback opcional para processar chunks em tempo real
            channel: Identificador da chamada (opcional)
            dynamic_variables: Variáveis dinâmica (opcional)
            
        Returns:
            AsyncGenerator que retorna cada chunk
        """
        request_body = {
            "prompt": prompt,
            "agent_id": agent_id,
            "conversation_id": conversation_id,
            "channel": channel.value,
            "dynamic_variables": dynamic_variables
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "X-API-Key": api_key
        }
        
        return Agent._stream_response(request_body, headers, conversation_id, debug=debug)
    
    @staticmethod
    async def _stream_response(request_body: Dict, headers: Dict, conversation_id: str, debug: bool = False) -> AsyncGenerator[Tuple[bool, AgentResponse], None]:
        """Generator assíncrono que entrega cada chunk como AgentResponse."""
        handshake = {}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    Agent.CHAT_STREAM_API_URL, 
                    json=request_body,
                    headers=headers
                ) as response:
                    if not response.ok:
                        error_msg = f"Erro na API de agentes: {response.status} {response.reason}"
                        yield AgentResponse(
                            engine="error",
                            conversation_id=conversation_id,
                            output=error_msg
                        )
                        return
                    
                    async for chunk in response.content.iter_chunks():
                        if chunk[0]:
                            text_chunk = chunk[0].decode('utf-8')

                            if text_chunk.startswith("__FINAL_STATE__"):
                                if debug:
                                    yield text_chunk
                                
                                continue
                            
                            if "engine" in text_chunk and "conversation_id" in text_chunk:
                                try:
                                    handshake = json.loads(text_chunk)
                                    continue
                                except json.JSONDecodeError:
                                    logger.error(f"Erro ao decodificar handshake: {text_chunk}")
                                    continue

                            chunk_data = {"output": text_chunk}
                            
                            if handshake.get("engine") == AgentEngine.operator.value:
                                try:
                                    chunk_data = json.loads(text_chunk)
                                except json.JSONDecodeError:
                                    pass
                            
                            response_obj = AgentResponse(
                                engine=handshake.get("engine", "error"),
                                conversation_id=handshake.get("conversation_id", "error"),
                                **chunk_data
                            )
                            
                            yield response_obj
        except Exception as e:
            error_msg = f"Erro ao chamar API de agentes em modo streaming: {str(e)}"
            yield AgentResponse(
                engine="error",
                conversation_id=conversation_id,
                output=error_msg
            )