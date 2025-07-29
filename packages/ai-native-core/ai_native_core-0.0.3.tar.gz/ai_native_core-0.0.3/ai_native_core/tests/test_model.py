import os

import pytest

from ai_native_core.model import last_model


@pytest.mark.asyncio
async def test_default_model():
    async for chunk in last_model.astream(
            "你是谁？",
            config={
                "configurable": {
                    "last_temperature": 0,
                    "last_max_tokens": 512,
                    "last_api_key": os.getenv('CHAT_MODEL_DEFAULT_API_KEY')
                }
            },
    ):
        print(chunk.content, end='')


@pytest.mark.asyncio
async def test_tencent_model():
    async for chunk in last_model.astream(
            "你是谁？",
            config={
                "configurable": {
                    "last_base_url": "https://api.lkeap.cloud.tencent.com/v1",
                    "last_model": "deepseek-v3-0324",
                    "last_temperature": 0,
                    "last_max_tokens": 512,
                    "last_api_key": os.getenv('TENCENT_DEEPSEEK_TOKEN')
                }
            },
    ):
        print(chunk.content, end='')
