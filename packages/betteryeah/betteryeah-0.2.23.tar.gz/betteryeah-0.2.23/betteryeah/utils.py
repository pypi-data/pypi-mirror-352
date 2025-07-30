import inspect
import json
import os
import aiohttp
from functools import wraps
from typing import get_origin, get_args, Union, AsyncGenerator

base_url = "https://ai-api.betteryeah.com/v1" if os.environ.get("GEMINI_SERVER_HOST") is None else os.getenv(
    "GEMINI_SERVER_HOST") + "/v1"


async def get_workspace_id():
    if os.environ.get("RUN_ARGS"):
        try:
            run_args = json.loads(os.environ.get("RUN_ARGS"))
            if run_args.get("workspace_id"):
                os.environ["workspace_id"] = run_args.get("workspace_id")
                return
        except Exception as e:
            pass
    if not os.getenv('API_KEY'):
        raise Exception(f"请设置api_key")
    endpoint = "/oapi/integration/get_workspace_id"
    async with aiohttp.ClientSession() as session:
        async with session.request("POST", f"{base_url}{endpoint}",
                                   json={"Authorization": f"{os.getenv('API_KEY')}"}) as response:
            result = await response.json()
            if result.get("code") == 200 and result.get("data"):
                os.environ["workspace_id"] = result.get("data").get("workspace_id")
            else:
                raise Exception(f"获取workspace_id失败,返回的结果:{result},请确认apikey是否正确")


async def request_build_base(data: dict, endpoint: str = "/integration"):
    if data.get("run_args") is None and os.getenv("RUN_ARGS"):
        data["run_args"] = os.getenv("RUN_ARGS")

    if not os.environ.get("workspace_id"):
        await get_workspace_id()
    headers = {
        "Authorization": f"{os.getenv('API_KEY')}",
        "Content-Type": "application/json",
        "Workspace-Id": os.environ.get("workspace_id")
    }

    url = f"{base_url}{endpoint}"
    return url, headers


async def send_request(method: str, data: dict, endpoint: str = "/oapi/integration", time_out=600) -> dict:
    timeout = aiohttp.ClientTimeout(total=time_out, sock_read=None)  # 禁用读取超时
    url, headers = await request_build_base(data, endpoint)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.request(method, url, json=data, headers=headers) as response:
            return await response.json()


async def send_request_stream(method: str, data: dict, endpoint: str = "/oapi/integration",
                              time_out=600) -> AsyncGenerator:
    timeout = aiohttp.ClientTimeout(total=time_out, sock_read=None)  # 禁用读取超时
    url, headers = await request_build_base(data, endpoint)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.request(method, url, json=data, headers=headers) as response:
            # 根据需要处理流式传输
            async for res in response.content:
                decoded_line = res.decode('utf-8').strip()
                if decoded_line.startswith("data:"):
                    data_content = decoded_line[5:].strip()
                    yield data_content


async def abcd(check: bool) -> Union[
    dict | AsyncGenerator]:
    if check:
        async def generator():
            yield 123

        return generator()
    else:
        return {}


def type_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        annotations = func.__annotations__
        all_args = inspect.getcallargs(func, *args, **kwargs)

        def check_type(val, exp_type):
            if val is None:
                # 如果值是None，只有在类型是Optional时才是合法的
                return get_origin(exp_type) is Union and type(None) in get_args(exp_type)
            origin = get_origin(exp_type)
            if origin is Union:
                # 如果类型是Union，检查是否至少有一个类型匹配
                return any(check_type(val, t) for t in get_args(exp_type))
            elif origin:
                # 处理其他泛型类型，如List或Dict
                if not isinstance(val, origin):
                    raise TypeError(
                        f"调用{func.__name__}方法的参数{arg}类型不正确,要求传入的类型为{origin.__name__},实际传入的类型为{type(val).__name__}")
                args_type = get_args(exp_type)
                if args_type and not all(check_type(item, args_type[0]) for item in val):
                    return False
                return True
            else:
                # 非泛型类型检查
                if not isinstance(val, exp_type):
                    raise TypeError(
                        f"调用{func.__name__}方法的参数{arg}类型不正确,要求传入的类型为{exp_type.__name__},实际传入的类型为{type(val).__name__}")
                return True

        for arg, value in all_args.items():
            expected_type = annotations.get(arg)
            if expected_type is None:
                continue  # 如果没有类型注解则跳过

            # 进行类型检查
            if not check_type(value, expected_type):
                raise TypeError(f"调用{func.__name__}方法的参数{arg}不符合类型要求。")

        return func(*args, **kwargs)

    return wrapper
