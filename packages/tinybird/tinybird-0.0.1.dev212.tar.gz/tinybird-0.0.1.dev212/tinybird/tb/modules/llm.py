import requests

from tinybird.tb.modules.feedback_manager import FeedbackManager


class LLMException(Exception):
    pass


class LLM:
    def __init__(
        self,
        host: str,
        user_token: str,
    ):
        self.host = host
        self.user_token = user_token

    def ask(self, system_prompt: str, prompt: str) -> str:
        """
        Calls the model with the given prompt and returns the response.

        Args:
            system_prompt (str): The system prompt to send to the model.
            prompt (str): The user prompt to send to the model.

        Returns:
            str: The response from the language model.
        """

        data = {"system": system_prompt, "prompt": prompt}

        response = requests.post(
            f"{self.host}/v0/llm",
            headers={"Authorization": f"Bearer {self.user_token}"},
            data=data,
        )

        if not response.ok:
            raise LLMException(FeedbackManager.error_request_failed(status_code=response.status_code))

        return response.json().get("result", "")
