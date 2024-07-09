from base64 import b64encode
from logging import getLogger

from openai import AzureOpenAI

logger = getLogger(__name__)


class OpenAiClient:
    def __init__(
        self,
        api_key: str,
        api_version: str,
        endpoint: str,
        gpt_model: str,
    ) -> None:
        self.api_key = api_key
        self.api_version = api_version
        self.endpoint = endpoint
        self.gpt_model = gpt_model

    def get_client(self) -> AzureOpenAI:
        return AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
        )

    def create_chat_completions_with_vision(
        self,
        system_prompt: str,
        user_prompt: str,
        image: bytes,
    ) -> str:
        encoded_image = b64encode(image).decode("ascii")

        response = self.get_client().chat.completions.create(
            model=self.gpt_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            },
                        },
                    ],
                },
            ],
            stream=False,
        )
        logger.info(response)
        return response.choices[0].message.content
