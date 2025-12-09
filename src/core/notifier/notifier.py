import asyncio
import json
from typing import Any, AsyncGenerator, Dict, Union

from fastapi import Request


class Notifier:
    """Gerencia a fila de eventos por ID de Usuário (Unicast)."""

    # Mapeia user_id (str ou int) para sua respectiva fila de mensagens
    # Usaremos Union[str, int] para ser flexível, mas o FastAPI/Dependência deve garantir o tipo.
    def __init__(self):
        self.listeners: Dict[Union[str, int], asyncio.Queue[Dict[str, Any]]] = {}

    async def push_to_user(
        self, user_id: Union[str, int], message: str, level: str, title: str = None
    ):
        """Envia uma mensagem APENAS para o cliente com o ID de Usuário especificado."""

        queue = self.listeners.get(user_id)
        if queue:
            message_data = {"message": message, "level": level, "title": title}
            await queue.put(message_data)
        else:
            # Isso é normal se o usuário estiver logado mas não tiver a aba com o SSE aberta
            print(
                f"Aviso: Usuário {user_id} não tem conexão SSE ativa para notificação."
            )

    async def subscribe(
        self, request: Request, user_id: Union[str, int]
    ) -> AsyncGenerator[str, None]:
        """Cria e gerencia a conexão SSE para um usuário específico."""

        # 1. Cria ou pega a fila (Associa a fila ao ID do usuário)
        # Se o usuário abrir 5 abas, todas usarão a mesma fila, ou você pode
        # criar uma ID única por conexão se quiser roteamento por sessão/aba.
        # Para unicast por usuário, a abordagem abaixo é a mais simples e comum:
        queue = self.listeners.setdefault(user_id, asyncio.Queue())
        print(
            f"Usuário {user_id} conectado. Total de ouvintes ativos: {len(self.listeners)}"
        )

        try:
            while True:
                message_data = await queue.get()
                yield f"data: {json.dumps(message_data)}\n\n"
                queue.task_done()

        except asyncio.CancelledError:
            pass
        finally:
            # 2. Quando o cliente desconecta, garantimos que a fila é limpa
            # Aqui fica um ponto de atenção: Se o usuário tiver múltiplas abas,
            # fechar uma aba pode desalocar a fila se usarmos 'del self.listeners[user_id]'.
            # Para evitar isso, a limpeza deve ser mais inteligente (ex: verificar se a fila está vazia
            # ou usar uma ID de sessão em vez de ID de usuário para a chave).
            # Para fins de demonstração, vamos apenas remover se for a única conexão restante.
            # Em produção, você pode preferir usar uma estrutura de Set[Queue] por usuário.

            # **Abordagem Simples (Pode ter problemas com múltiplas abas):**
            # del self.listeners[user_id]

            # **Abordagem Reativa:** A fila permanecerá até que o servidor se reinicie
            # ou que você adicione lógica para fechar a fila quando todas as abas sumirem.
            # Para este exemplo, deixamos a fila existir e ela será limpa na próxima conexão,
            # a não ser que a memória se torne um problema.
            print(
                f"Usuário {user_id} desconectou. Total de ouvintes ativos: {len(self.listeners)}"
            )


notifier = Notifier()
