import asyncio

from test import get_betteryeah
from betteryeah.knowledge import HitStrategyType, OutPutType


async def test_search_knowledge():
    better_yeah = get_betteryeah()
    result = await better_yeah.knowledge.search_knowledge(
        search_content="重庆美食",
        partition_id=571,
        file_ids=[],
        tags=None,
        output_type=OutPutType.JSON,
        hit_strategy=HitStrategyType.MIX,
        max_result_num=6,
        ranking_strategy=True
    )
    print(result.data.match_contents)


async def test_insert_knowledge():
    better_yeah = get_betteryeah()
    result = await better_yeah.knowledge.insert_knowledge(
        content="重庆大盘鸡步骤：把鸡肉赶在锅的一边，在锅底放入豆瓣、老干妈、青花椒、蒜瓣、老姜、八角、冰糖，进行翻炒。接着倒入啤酒，将鸡肉淹没，加老抽、生抽，盖锅用中火烹煮。",
        file_id=4151,
        partition_id=571
    )
    print(result)


async def test_case():
    better_yeah = get_betteryeah()
    import re
    import json
    from betteryeah import OutPutType, HitStrategyType

    file_ids = []

    search_result = await better_yeah.knowledge.search_knowledge(
        search_content="重庆",
        partition_id=4930,
        tags=[],
        file_ids=file_ids,
        output_type=OutPutType.JSON,
        hit_strategy=HitStrategyType.MIX,
        max_result_num=3,
        ranking_strategy=False
    )

    results = []
    for r in search_result.data.match_contents:
        content = r.content
        content = re.sub(r"!\\[.*?\\]\\(.*?\\)", " ", content).strip()
        result = {
            "file_id": r.file_id,
            "file_name": r.file_name,
            "content": content,
        }
        results.append(result)

    results = "\\n".join([json.dumps(r, ensure_ascii=False) for r in results])
    print(results)


if __name__ == "__main__":
    asyncio.run(test_case())
    # asyncio.run(test_insert_knowledge())
