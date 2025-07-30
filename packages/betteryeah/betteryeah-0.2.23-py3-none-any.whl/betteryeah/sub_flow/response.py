from dataclasses import dataclass
from typing import Any


@dataclass
class SubFlowExecuteOutput:
    # 流程id
    flow_id: str
    # 执行任务id
    task_id: str
    # 执行结果
    run_result: str
    # 执行时长
    durationTime: Any
    # 执行信息
    message: str

    status: str
