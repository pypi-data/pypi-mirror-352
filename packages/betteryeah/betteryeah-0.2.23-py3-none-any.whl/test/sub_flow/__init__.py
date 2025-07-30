import asyncio
from test import get_betteryeah


async def test_sub_flow_execute():
    better_yeah = get_betteryeah()
    result = await better_yeah.sub_flow.execute(
        flow_id="acb5888f3e9e44b786d387131bab5cdd",
        parameter={"city": "杭州"}
    )
    print(result)


async def test_flow_execute():
    better_yeah = get_betteryeah()
    result = await better_yeah.flow.execute(
        flow_id="acb5888f3e9e44b786d387131bab5cdd",
        parameter={"city": "杭州"}
    )
    print(result)


async def test_flow():
    await test_sub_flow_execute()
    await test_flow_execute()


if __name__ == "__main__":
    asyncio.run(test_flow())
