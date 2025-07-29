import os
from typing import Optional

from openai import AsyncAzureOpenAI

from .azure_ai_language_utils import TextAnalysis

client = AsyncAzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    api_key=os.getenv("AZURE_OPENAI_KEY", ""),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", ""),
)
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")


async def get_text_analysis(system_prompt: str, user_prompt: str) -> Optional[TextAnalysis]:
    completion = await client.beta.chat.completions.parse(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=TextAnalysis,
    )

    event = completion.choices[0].message.parsed
    return event
