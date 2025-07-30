import asyncio

from test import get_betteryeah


async def test_execute_database():
    base_id = "pj9xrcczl510cx8"
    executable_sql = "SELECT count(*) FROM user where name = '小黑' LIMIT 2"
    better_yeah = get_betteryeah()
    result = await better_yeah.database.execute_database(
        base_id=base_id, executable_sql=executable_sql
    )
    print(f"查询数据库结果为：{result.data}")


# 运行测试
if __name__ == "__main__":
    asyncio.run(test_execute_database())
