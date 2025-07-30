import os
import ollama
import re


class Chatbot:
    def __init__(self, name: str, *args, **kwargs):
        system_prompt = """
            Eres un Chatbot y asistente, especializado en responder preguntas. Tu tarea es responder preguntas basadas en el contexto proporcionado. 
            Utiliza el contexto para generar respuestas precisas y relevantes. Utiliza siempre un tono formal y profesional. Si no encuentras información relevante en el contexto, responde con "No tengo información suficiente para responder a esa pregunta". Responde siempre en el mismo idioma que el de la pregunta.
        """
        bots_names = [model.model for model in ollama.list()["models"]]
        if name not in bots_names:
            raise ValueError(
                f"The model '{name}' is not available. Available models in Ollama are: {', '.join(bots_names)}"
            )
        self.system_prompt = kwargs.get("system_prompt", system_prompt)
        self.name = name

    def __call__(self, context: str, question: str) -> str:
        response = self._generate_answer(context, question)
        response = self._posprocessing_answer(response)
        return response

    def _generate_answer(self, context: str, question: str) -> str:
        prompt = self._generate_prompt(context, question)
        response = ollama.chat(
            model=self.name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return response["message"]["content"]

    def _generate_prompt(self, context: str, question: str) -> str:
        prompt = f"""{self.system_prompt}

                    Contexto:
                    {context}

                    Pregunta:
                    {question}

                    Respuesta:
                    """
        return prompt

    def _posprocessing_answer(self, response, return_thinking=False):
        match = re.search(r"<think>(.*?)</think>\s*(.*)", response, flags=re.DOTALL)

        if match:
            thinking = match.group(1).strip()
            response = match.group(2).strip()
        else:
            thinking = None
            response = response
        if return_thinking:
            return response, thinking
        else:
            return response
