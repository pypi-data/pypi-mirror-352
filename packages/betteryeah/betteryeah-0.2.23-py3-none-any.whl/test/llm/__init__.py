import asyncio
import json
import os

from test import get_betteryeah
from betteryeah import Model


async def test_llm():
    better_yeah = get_betteryeah()
    result = await better_yeah.llm.chat(
        system_prompt="介绍一下重庆的特色美食",
        model="gpt-4o",
        json_mode=False,
        temperature=0.7,
        stream=False
    )
    print(result)


async def test_llm_stream():
    better_yeah = get_betteryeah()
    async for msg in await better_yeah.llm.chat(
            system_prompt="介绍一下重庆的特色美食",
            model="gpt-3.5-turbo",
            json_mode=False,
            temperature=0.7,
            stream=True):
        print(msg)


async def test_get_available_models():
    better_yeah = get_betteryeah()
    result = await better_yeah.llm.get_available_models()
    print(result.data)


async def test_case():
    better_yeah = get_betteryeah()
    result = await better_yeah.llm.chat(
        system_prompt="介绍一下重庆的特色美食",
        json_mode=False,
        model='anthropic.claude-3.5-sonnet',
        temperature=0.7
    )
    print(result)


async def test_case2():
    better_yeah = get_betteryeah()
    userInput_data = await better_yeah.llm.chat(system_prompt="介绍一下重庆的特色美食,20字以内",
                                                model=Model.gpt_4_turbo)
    print(userInput_data)


if __name__ == "__main__":
    asyncio.run(test_case())
    # asyncio.run(test_llm_stream())
    # asyncio.run(test_get_available_models())
