import json
from inspect import signature

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool
from pydantic import ValidationError
from typing_extensions import Any, Optional, override, Dict


def _get_runnable_config_param(func: Any) -> Optional[str]:
    """检查函数是否接受 RunnableConfig 类型的参数。"""
    for param_name, param in signature(func).parameters.items():
        # 检查参数类型是否是 RunnableConfig，并且是位置或关键字参数
        if param.kind == param.POSITIONAL_OR_KEYWORD and param.annotation == RunnableConfig:
            return param_name  # 如果找到，返回参数名
    return None  # 否则返回 None


# 定义你的自定义工具类，并重写 run 方法
class SynchronizedStructuredTool(StructuredTool):
    """
    一个自定义的 StructuredTool，它重写了 run 方法，
    以包含 MCP 同步逻辑，同时正确解析 args_schema。
    """

    # 你可以在这里添加特定的 MCP 相关属性，如果后续需要的话
    @override  # 这是一个装饰器，表明这个方法重写了父类的方法
    def run(
            self,
            *args: Any,  # 捕获所有位置参数，例如 LLM 返回的 action_input 字符串
            config: RunnableConfig,  # 运行配置，通常包含回调管理器等信息
            run_manager: Optional[CallbackManagerForToolRun] = None,  # 回调管理器，用于报告工具运行状态
            **kwargs: Any,  # 捕获所有关键字参数
    ) -> Any:
        """
        用于 MCP 同步的自定义 run 方法，
        同时正确处理 StructuredTool 的 args_schema 解析。
        """
        # 如果工具的核心功能函数 (self.func) 未设置，则回退到父类的 run 方法
        if not self.func:
            return super().run(*args, config=config, run_manager=run_manager, **kwargs)

        # --- 参数解析逻辑开始 ---
        # 对于 StructuredTool，大语言模型 (LLM) 的 `action_input` 通常作为 args[0] 传递进来，
        # 并且它通常是一个 JSON 字符串。
        # 如果工具是直接通过关键字参数调用，那么 args 可能为空。

        parsed_input_dict: Dict[str, Any]  # 声明一个字典变量，用于存储解析后的输入

        # 检查工具是如何被调用的
        if not args and kwargs:
            # 情况 1：工具直接通过关键字参数调用，这些参数与 args_schema 匹配。
            # 示例：tool(query="llmpos")
            # 在这种情况下，kwargs 已经包含了拆包后的参数，可以直接使用。
            parsed_input_dict = kwargs
        elif args and len(args) == 1 and isinstance(args[0], str):
            # 情况 2：LLM 的 action_input 作为 JSON 字符串出现在 args[0] 中。
            # 示例：{"action_input": '{"query": "llmpos"}'}
            raw_tool_input_str = args[0]  # 获取原始的 JSON 字符串输入
            try:
                parsed_input_dict = json.loads(raw_tool_input_str)  # 尝试将 JSON 字符串解析成 Python 字典
            except json.JSONDecodeError:
                # 如果解析失败（不是有效的 JSON），则抛出错误
                raise ValueError(f"工具输入不是有效的 JSON 字符串: {raw_tool_input_str}")
        elif args and len(args) == 1 and isinstance(args[0], dict):
            # 情况 3：LLM 的 action_input 直接作为字典出现在 args[0] 中。
            # 这通常发生在代理（agent）已经解析了 JSON 字符串的情况下。
            # 示例：{"action_input": {"query": "llmpos"}}
            parsed_input_dict = args[0]
        else:
            # 如果输入格式不符合上述任何一种情况，则认为是非预期的输入，并抛出错误。
            # 这可能表明代理/链调用工具的方式有问题。
            raise ValueError(f"非预期的工具输入格式。args: {args}, kwargs: {kwargs}")

        # --- 可选：处理 LLM 输出不一致导致嵌套的逻辑（如果需要） ---
        # 如果 LLM 有时会输出 {"query": {"query": "llmpos"}} 这种嵌套格式（尽管你已经给出了指令），
        # 你可以尝试在这里进行“扁平化”处理。
        # 注意：这只是一种临时的补救措施；最好的方法是修正 LLM 的输出。
        if isinstance(parsed_input_dict, dict) and "query" in parsed_input_dict and \
                isinstance(parsed_input_dict["query"], dict) and "query" in parsed_input_dict["query"]:
            parsed_input_dict = {"query": parsed_input_dict["query"]["query"]}
        # --- 结束可选的扁平化逻辑 ---

        # 根据 args_schema 验证解析后的字典。
        try:
            # self.args_schema 是你为工具定义的 Pydantic 模型（例如 DatasetRetrievalInput）。
            # parse_obj 方法会根据模型定义验证并创建一个 Pydantic 模型实例。
            validated_input_model = self.args_schema.parse_obj(parsed_input_dict)
        except ValidationError as e:
            # 如果 Pydantic 验证失败，打印详细错误信息并抛出 ValueError
            print(f"工具输入 Pydantic 验证错误: {e.errors()}")
            raise ValueError(f"工具输入验证失败: {e.errors()}，输入为: {parsed_input_dict}")
        except Exception as e:
            # 捕获其他可能的解析错误
            print(f"解析工具输入时出错: {e}")
            raise ValueError(f"解析工具输入时出错: {e}，输入为: {parsed_input_dict}")

        # 从验证后的 Pydantic 模型中提取出传递给核心函数 (self.func) 的独立参数。
        func_kwargs = validated_input_model.dict()

        # 添加回调管理器 (callbacks) 和配置 (config) 参数，如果核心函数接受它们的话。
        if run_manager and signature(self.func).parameters.get("callbacks"):
            func_kwargs["callbacks"] = run_manager.get_child()  # 获取子回调管理器
        if config_param := _get_runnable_config_param(self.func):
            func_kwargs[config_param] = config  # 添加配置参数

        # --- MCP 同步逻辑在这里 ---
        # 这里是你可以添加特定 MCP 同步代码的地方。
        # 例如：
        # if self.mcp_sync_enabled:
        #     self._perform_mcp_sync(func_kwargs) # 调用你的同步函数

        # 调用实际的核心函数 (self.func)，并传入正确解析和处理后的参数。
        return self.func(**func_kwargs)
