import os
from typing import Optional

import dotenv
from openai import OpenAI
from mofa.utils.files.dir import get_relative_path
from mofa.kernel.utils.util import load_agent_config
dotenv.load_dotenv()


class OpenAIClient:
    def __init__(self, inputs, **kwargs) -> None:
        # yaml_path = get_relative_path(__file__, sibling_directory_name='mcp_llm/configs', target_file_name='chat_session.yml')
        self.api_key = inputs["model_api_key"]
        self.model_name = inputs['model_name']
        if "model_api_url" in inputs.keys():
            base_url = inputs["model_api_url"]
            self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=self.api_key, **kwargs)

    def get_response(self, messages: list[dict[str, str]]) -> str:
        """Get a response from the LLM (qwen).

        Args:
            messages: A list of message dictionaries.

        Returns:
            The LLM's response as a string.
        """
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
        )
        return completion.choices[0].message.content


if __name__ == "__main__":
    client = OpenAIClient()
    # Testing.
    print(client.get_response([{"role": "user", "content": "你是谁？"}]))
