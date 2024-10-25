import os
import time
from typing import Literal, TypedDict
from dotenv import load_dotenv

import openai
from openai.types.beta import ThreadDeleted
from openai.types.beta.threads import Message
from openai.types.beta.threads.run import Run

load_dotenv()

RunPendingStatus = ["queued", "in_progress"]
RunSuccessStatus = ["completed"]
RunErrorStatus = ["cancelled", "expired", "failed"]
RunFinalStatus = RunSuccessStatus + RunErrorStatus + ["requires_action"]


class SimpleMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class UserThread:
    assistant_id: str

    def __init__(self) -> None:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if openai.api_key is None:
            raise Exception("OPENAI_API_KEY não está definido")

        assistant_id = os.getenv("OPENAI_ASSISTANT_ID")

        if assistant_id is None:
            raise Exception("OPENAI_ASSISTANT_ID não está definido")

        self.assistant_id = assistant_id

        self.client = openai.OpenAI()

    def ask(self,
            message: str,
            thread_id: str | None = None) -> tuple[str, str]:
        """Faz uma pergunta ao assistente e retorna uma resposta

        Args:
            message (str): A mensagem a ser enviada ao assistente
            thread_id (str|None, optional): O ID do thread a ser enviado. Defaults to None.

        Returns:
            str: A resposta do assistente e a ID da thread
        """
        if message is None or len(message) <= 1:
            raise Exception("Mensagem não pode ser nula")

        if thread_id is None:
            return self.create_thread(message)

        return self.message_thread_or_create(thread_id, message)

    def _get_messages(self,
                      thread_id: str,
                      asc: bool = False) -> list[Message]:
        """Obtém as mensagens de um thread

        Args:
            thread_id (str): O ID do thread a ser obtido
            asc (bool, optional): Se as mensagens devem ser ordenadas em ordem ascendente (mais antiga primeiro). Defaults to False.

        Returns:
            list[Message]: As mensagens do thread

        Raises:
            Exception: Se o thread_id não existir na OpenAI
        """
        order: Literal["asc", "desc"] = "asc" if asc else "desc"

        try:
            messages = self.client.beta.threads.messages.list(thread_id,
                                                              order=order)
            return messages.data
        except openai.NotFoundError:
            raise Exception(f"Thread {thread_id} não existe")
        except Exception as e:
            raise e

    def list_messages(self,
                      thread_id: str,
                      asc: bool = False) -> list[SimpleMessage]:
        messages = self._get_messages(thread_id, asc)

        msg_list: list[SimpleMessage] = []
        for message in messages:
            content = message.content[0]
            if content.type == "text":
                msg_list.append({
                    "role": message.role,
                    "content": content.text.value
                })
            elif content.type == "refusal":
                msg_list.append({
                    "role": message.role,
                    "content": content.refusal
                })

        return msg_list

    def delete_thread(self, thread_id: str) -> None:
        """Deleta o thread do usuário

        Args:
            thread_id (str): O ID do thread a ser deletado
        """
        response: ThreadDeleted = self.client.beta.threads.delete(thread_id)
        if not response.deleted:
            raise Exception(f"Thread {thread_id} não pode ser deletada")

    def message_thread(self, thread_id: str, message: str) -> tuple[str, str]:
        """Salva uma mensagem no thread do usuário

        Args:
            thread_id (str): O ID do thread a ser salvo
            message (str): A mensagem a ser salva

        Raises:
            Exception: Se houver um erro ao salvar a mensagem
        """
        self.client.beta.threads.messages.create(
            thread_id,
            role="user",
            content=message,
        )

        run = self.client.beta.threads.runs.create(
            thread_id,
            assistant_id=self.assistant_id,
        )

        if run.status == "completed":
            return thread_id, self.get_last_message(thread_id, "assistant")

        return thread_id, self._wait_run_and_get_response(thread_id, run.id)

    def message_thread_or_create(self, thread_id: str,
                                 message: str) -> tuple[str, str]:
        """Salva uma mensagem no thread do usuário ou cria um novo thread se o thread_id não existir

        Args:
            thread_id (str): O ID do thread a ser salvo
            message (str): A mensagem a ser salva
        """
        try:
            return self.message_thread(thread_id, message)
        except Exception:
            return self.create_thread(message)

    def create_thread(self, message: str) -> tuple[str, str]:
        run = self.client.beta.threads.create_and_run(
            assistant_id=self.assistant_id,
            thread={
                "messages": [
                    {
                        "role":
                        "assistant",
                        "content":
                        "Olá, bem vindo! Eu sou a Pri, sua assistente virtual especialista em privacidade e proteção de dados. Como posso ajudar você hoje?"
                    },
                    {
                        "role": "user",
                        "content": message
                    },
                ]
            })

        if run.status == "completed":
            return run.thread_id, self.get_last_message(
                run.thread_id, "assistant")

        return run.thread_id, self._wait_run_and_get_response(
            run.thread_id, run.id)

    def _wait_run_and_get_response(self,
                                   thread_id: str,
                                   run_id: str,
                                   recursion_level: int = 0) -> str:
        run: Run = self.client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                          run_id=run_id)

        if run.status in RunSuccessStatus:
            return self.get_last_message(thread_id, "assistant")
        elif run.status in RunErrorStatus:
            raise Exception(f"Run {run_id} finalizado com status {run.status}")
        elif run.status in RunPendingStatus and recursion_level < 5:
            time.sleep(2 + recursion_level * 2)
            return self._wait_run_and_get_response(thread_id, run_id,
                                                   recursion_level + 1)

        raise Exception(f"Run retrieval max recursion level reached.")

    def get_last_message(
            self,
            thread_id: str,
            role: Literal["user", "assistant"] | None = None) -> str:
        messages = self._get_messages(thread_id)

        for message in messages:
            if role is None or message.role == role:
                for content in message.content:
                    if content.type == "text":
                        return content.text.value
                    elif content.type == 'refusal':
                        return content.refusal

                    raise Exception(
                        f"Tipo de conteúdo não suportado: {content.type}")

        raise Exception("Nenhuma mensagem encontrada.")
