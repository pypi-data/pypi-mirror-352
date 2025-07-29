"""LLM Service module for handling language model interactions."""

import os
from typing import Optional, Dict, Any, List, Literal
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


class LLMService:
    """Service for handling interactions with Language Models."""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initialize the LLM service.

        Args:
            model (str): The model identifier to use for completions.
                        Defaults to "gpt-3.5-turbo".
        """
        load_dotenv()  # Load environment variables from .env file

        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def get_completion(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """Get a completion from the language model.

        Args:
            prompt (str): The prompt to send to the model
            temperature (float, optional): Sampling temperature. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens to generate.
            stop (List[str], optional): List of strings where the model should stop generating.
            **kwargs: Additional parameters to pass to the completion API.

        Returns:
            str: The generated completion text.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error getting completion: {str(e)}")

    def get_chat_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """Get a chat completion from the language model.

        Args:
            messages (List[ChatCompletionMessageParam]): List of message dictionaries with 'role' and 'content'.
            temperature (float, optional): Sampling temperature. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens to generate.
            stop (List[str], optional): List of strings where the model should stop generating.
            **kwargs: Additional parameters to pass to the completion API.

        Returns:
            str: The generated completion text.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error getting chat completion: {str(e)}")
