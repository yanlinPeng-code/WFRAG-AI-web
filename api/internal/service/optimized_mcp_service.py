import asyncio
import json
import threading
import time
from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from injector import inject
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing_extensions import List, Any

from internal.core.mcp.mcp_client import McpCache, McpToolWrapper
from internal.model import McpToolProvider
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class OptimizedMCPServiceWithFucCache:
    """针对包含函数对象的MCP工具的优化服务"""
    db: SQLAlchemy
    cache: McpCache

    def get_langchain_tools_by_mcp_tool_config(self,
                                               mcp_tools: Any):
        """优化的工具获取方法"""

        try:
            # 构建MCP配置
            if type(mcp_tools) is list:
                total_mcp_schema = self._build_mcp_schema(mcp_tools)

                # 尝试从缓存获取
                cached_tools = self.cache.get_cached_tools(
                    total_mcp_schema,
                    tool_builder_func=self._rebuild_tools_from_metadata
                )

                if cached_tools is not None:
                    return cached_tools

                # 缓存未命中，重新获取
                print("[MCP SERVICE] 缓存完全未命中，重新获取工具...")
                start_time = time.time()

                tools = self._fetch_tools_from_mcp(total_mcp_schema)

                # 包装工具对象以便缓存
                wrapped_tools = [McpToolWrapper(tool) for tool in tools]

                # 缓存结果
                self.cache.set_cached_tools(total_mcp_schema, wrapped_tools)

                end_time = time.time()
                print(f"[MCP SERVICE] 获取工具完成，耗时: {end_time - start_time:.2f}秒")

                return wrapped_tools
            else:
                DYNAMIC_ENV_KEYS = {"PATH", "HOME", "USER", "TMP", "TEMP", "HOSTNAME",
                                    "PWD"}  # Add any others you find are changing
                total_mcp_schema = {}
                for server_name, server_config in mcp_tools.get("mcpServers").items():
                    original_env = server_config.get("env", {})

                    # Create a new, filtered environment dictionary
                    cleaned_env = {
                        k: v for k, v in original_env.items()
                        if k not in DYNAMIC_ENV_KEYS
                    }
                    target_server_config = {
                        "command": server_config.get("command"),
                        "args": server_config.get("args", []),
                        "env": cleaned_env,  # Use the cleaned environment here
                        "transport": server_config.get("transport", {}),
                    }
                    total_mcp_schema[server_name] = target_server_config
                # 尝试从缓存获取
                cached_tools = self.cache.get_cached_tools(
                    total_mcp_schema,
                    tool_builder_func=self._rebuild_tools_from_metadata
                )

                if cached_tools is not None:
                    return cached_tools

                # 缓存未命中，重新获取
                print("[MCP SERVICE] 缓存完全未命中，重新获取工具...")
                start_time = time.time()

                tools = self._fetch_tools_from_mcp(total_mcp_schema)

                # 包装工具对象以便缓存
                wrapped_tools = [McpToolWrapper(tool) for tool in tools]

                # 缓存结果
                self.cache.set_cached_tools(total_mcp_schema, wrapped_tools)

                end_time = time.time()
                print(f"[MCP SERVICE] 获取工具完成，耗时: {end_time - start_time:.2f}秒")

                return wrapped_tools

        except Exception as e:
            print(f"[MCP SERVICE] 获取工具失败: {e}")
            raise

    def _build_mcp_schema(self, mcp_tools: list[dict]) -> dict:
        """
        根据mcp_tools列表构建聚合的mcp_schema，并确保其可用于缓存。
        mcp_tools: [{"id": "provider_a"}, {"id": "provider_b"}]
        """
        mcp_provider_ids = [mcp_provider.get("id") for mcp_provider in mcp_tools if mcp_provider.get("id")]

        if not mcp_provider_ids:
            # It's better to log a warning and return an empty schema if no IDs are found
            # rather than raising an exception which might break the flow if no tools are intended.
            print("WARNING: No valid mcp provider IDs found in mcp_tools config.")
            return {}

        # Assuming McpToolProvider is properly imported and self.db.session is your SQLAlchemy session
        mcp_providers = self.db.session.query(McpToolProvider).filter(
            McpToolProvider.id.in_(mcp_provider_ids)
        ).all()

        if not mcp_providers:
            print(f"WARNING: No mcp providers found in DB for IDs: {mcp_provider_ids}")
            return {}

        total_mcp_schema = {}
        # Define environment variables that are dynamic and should be excluded from caching
        DYNAMIC_ENV_KEYS = {"PATH", "HOME", "USER", "TMP", "TEMP", "HOSTNAME",
                            "PWD"}  # Add any others you find are changing

        for mcp_provider in mcp_providers:
            try:
                mcp_schema_from_db = json.loads(mcp_provider.mcp_schema)
                mcp_servers = mcp_schema_from_db.get("mcpServers", {})

                for server_name, server_config in mcp_servers.items():
                    original_env = server_config.get("env", {})

                    # Create a new, filtered environment dictionary
                    cleaned_env = {
                        k: v for k, v in original_env.items()
                        if k not in DYNAMIC_ENV_KEYS
                    }
                    target_server_config = {
                        "command": server_config.get("command"),
                        "args": server_config.get("args", []),
                        "env": cleaned_env,  # Use the cleaned environment here
                        "transport": server_config.get("transport", {}),
                    }
                    total_mcp_schema[server_name] = target_server_config
            except (json.JSONDecodeError, AttributeError, KeyError) as e:
                print(f"ERROR: Failed to process mcp_provider {getattr(mcp_provider, 'id', 'N/A')}: {e}")
                continue
        print("total_mcp_schema:", total_mcp_schema)
        return total_mcp_schema

    def _fetch_tools_from_mcp(self, mcp_schema: dict):
        """从MCP获取工具（原有逻辑）"""

        try:
            tools = asyncio.run(self.get_mcp_tools(mcp_schema))
        except RuntimeError as e:
            if "cannot be called from a running event loop" in str(e):
                loop = asyncio.get_event_loop()
                tools = loop.run_until_complete(self.get_mcp_tools(mcp_schema))
            else:
                raise e
        return tools

    def _rebuild_tools_from_metadata(self, metadata_list: List[dict], mcp_schema: dict):
        """从元数据重建工具对象"""
        print(f"[REBUILD] 开始从元数据重建 {len(metadata_list)} 个工具")

        try:
            # 重新获取完整的工具对象
            fresh_tools = self._fetch_tools_from_mcp(mcp_schema)

            # 包装为可缓存的工具
            wrapped_tools = [McpToolWrapper(tool) for tool in fresh_tools]

            print(f"[REBUILD] 重建完成，获得 {len(wrapped_tools)} 个工具")
            return wrapped_tools

        except Exception as e:
            print(f"[REBUILD] 重建工具失败: {e}")
            # 如果重建失败，返回空的工具对象（仅包含元数据）
            return [self._create_placeholder_tool(metadata) for metadata in metadata_list]

    def _create_placeholder_tool(self, metadata: dict):
        """创建占位符工具（仅用于元数据展示）"""

        class PlaceholderTool:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
                self.func = None  # 没有实际功能

        return PlaceholderTool(**metadata)

    # 异步预热缓存
    def preheat_cache_sync(self, common_configs: List[List[dict]], max_workers: int = 3):
        """同步版本的预热缓存 - Flask兼容"""
        print(f"[PREHEAT] 开始预热 {len(common_configs)} 个常用配置")
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有预热任务
            future_to_config = {
                executor.submit(self._preheat_single_config_sync, config): config
                for config in common_configs
            }

            # 等待所有任务完成
            completed = 0
            for future in as_completed(future_to_config):
                config = future_to_config[future]
                try:
                    future.result()  # 获取结果，如果有异常会抛出
                    completed += 1
                    print(f"[PREHEAT] 预热进度: {completed}/{len(common_configs)}")
                except Exception as e:
                    print(f"[PREHEAT] 预热配置失败: {e}")

        end_time = time.time()
        print(f"[PREHEAT] 预热完成，总耗时: {end_time - start_time:.2f}秒")

    def _preheat_single_config_sync(self, config: List[dict]):
        """同步版本的单个配置预热"""
        try:
            # 直接调用获取工具的方法
            self.get_langchain_tools_by_mcp_tool_config(config)
            print(f"[PREHEAT] 配置预热成功: {len(config)} 个工具")
        except Exception as e:
            print(f"[PREHEAT] 预热配置失败: {e}")
            raise

    def preheat_cache_background(self, common_configs: List[List[dict]]):
        """后台线程预热缓存 - 不阻塞Flask请求"""

        def background_preheat():
            try:
                self.preheat_cache_sync(common_configs)
            except Exception as e:
                print(f"[PREHEAT] 后台预热失败: {e}")

        # 在后台线程中运行预热
        thread = threading.Thread(target=background_preheat, daemon=True)
        thread.start()
        print("[PREHEAT] 后台预热任务已启动")
        return thread

    def get_cache_statistics(self):
        """获取缓存统计"""
        return self.cache.get_cache_stats()

    def clear_all_caches(self):
        """清空所有缓存"""
        self.cache.clear_cache()

    @classmethod
    async def get_mcp_tools(cls, mcp_tool_config: dict):
        """Get MCP tools with proper resource management"""
        client = MultiServerMCPClient(mcp_tool_config)
        try:
            tools = await client.get_tools()
            return tools
        finally:
            # Fix: Close the client, not the result of get_tools()
            try:
                if hasattr(client, 'close'):
                    if asyncio.iscoroutinefunction(client.close):
                        await client.close()
                    else:
                        client.close()
            except Exception:
                pass
