import hashlib
import json
import re
import threading
import time

import redis
from langchain_core.tools import StructuredTool
from typing_extensions import Callable, Any, List


class McpToolWrapper(StructuredTool):
    """MCP的包装类-用于缓存和序列化"""

    def __init__(self, origin_tool: StructuredTool):
        # Pass the fields required by StructuredTool to its constructor.
        # This is how Pydantic models get initialized correctly.
        super().__init__(
            name=origin_tool.name,
            description=origin_tool.description,
            args_schema=origin_tool.args_schema,
            func=origin_tool.func,  # CRITICAL: use 'func' not 'fuc'
            response_format=getattr(origin_tool, "response_format", 'content_and_artifact'),
            # response_format might be optional in StructuredTool's init depending on version
        )
        # Store the original tool if you need to access other properties
        self._origin_tool = origin_tool

    def to_serializable_dict(self) -> dict:
        """转换为可序列化的字典（不包含函数）"""
        return {
            'name': self.name,
            'description': self.description,
            'args_schema': self.args_schema,
            'response_format': self.response_format,
        }

    def __call__(self, *args, **kwargs):
        if self.func:
            return self.func(*args, **kwargs)
        return None


class McpCache:
    """高级MCP工具缓存 - 支持多级缓存策略"""

    def __init__(self,
                 redis_client=None,
                 memory_ttl: int = 1800,  # 内存缓存10分钟
                 redis_ttl: int = 1800,  # Redis缓存30分钟
                 max_memory_items: int = 100,
                 ):
        # redis缓存(存储工具的元数据)
        from app.http.app import injector
        from redis import Redis
        redis_client = injector.get(Redis)
        self.redis_client = redis_client
        self.redis_ttl = redis_ttl

        # 内存缓存(存储工具的完整对象)
        self.memory_cache = {}
        self.memory_timestamps = {}
        self.memory_ttl = memory_ttl
        self.max_memory_items = max_memory_items

        # 线程锁
        self.lock = threading.RLock()

        # 统计信息
        self.stats = {
            'memory_hits': 0,
            'redis_hits': 0,
            'misses': 0,
            'rebuilds': 0,

        }

    def _get_cache_key(self, mcp_schema: dict) -> str:
        """
        生成缓存键。
        此方法会在生成键之前，从传入的 mcp_schema 中，
        针对 'env' 字段，仅保留以 '_API_KEY' 结尾的键。
        """

        API_KEY_PATTERN = r"^[A-Z0-9_]+_API_KEY$"

        cleaned_mcp_schema = json.loads(json.dumps(mcp_schema))

        # Iterate through the top-level server configurations (e.g., 'amap-maps')
        for server_name, server_config in cleaned_mcp_schema.items():
            if "env" in server_config and isinstance(server_config["env"], dict):
                original_env = server_config["env"]
                # Create a new, filtered environment dictionary
                # This time, we only INCLUDE keys that match the API_KEY_PATTERN
                filtered_env = {
                    k: v for k, v in original_env.items()
                    if re.fullmatch(API_KEY_PATTERN, k)  # Only keep if it matches the API_KEY pattern
                }
                server_config["env"] = filtered_env

        print("mcp_schema (after API key filtering in _get_cache_key):", cleaned_mcp_schema)
        schema_str = json.dumps(cleaned_mcp_schema, sort_keys=True)
        print("schema_str (after API key filtering in _get_cache_key):", schema_str)
        return hashlib.md5(schema_str.encode()).hexdigest()[:16]

    def _cleanup_memory_cache(self):
        """清理过期的内存缓存"""
        current_time = time.time()
        expired_keys = []

        for key, timestamp in self.memory_timestamps.items():
            if current_time - timestamp > self.memory_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            self.memory_cache.pop(key, None)
            self.memory_timestamps.pop(key, None)

        # LRU清理
        if len(self.memory_cache) > self.max_memory_items:
            sorted_keys = sorted(
                self.memory_timestamps.keys(),
                key=lambda k: self.memory_timestamps[k]
            )
            keys_to_remove = sorted_keys[:len(self.memory_cache) - self.max_memory_items]
            for key in keys_to_remove:
                self.memory_cache.pop(key, None)
                self.memory_timestamps.pop(key, None)

    def get_cached_tools(self, mcp_schema: dict, tool_builder_func: Callable = None):
        """
        获取缓存的工具
        mcp_schema: MCP配置
        tool_builder_func: 工具构建函数，用于从元数据重建工具对象
        """
        cache_key = self._get_cache_key(mcp_schema)

        print(f"[CACHE] 尝试获取缓存: {cache_key}")
        print(self.memory_cache)
        print(self.memory_timestamps)
        current_time = time.time()

        with self.lock:
            self._cleanup_memory_cache()

            # 1. 尝试内存缓存（最快）
            if cache_key in self.memory_cache:
                timestamp = self.memory_timestamps.get(cache_key, 0)
                if current_time - timestamp < self.memory_ttl:
                    self.stats['memory_hits'] += 1
                    print(f"[CACHE] 内存缓存命中: {cache_key}")
                    return self.memory_cache[cache_key]
            #
            # # 2. 尝试弱引用缓存
            # if cache_key in self.weak_cache:
            #     self.stats['memory_hits'] += 1
            #     print(f"[CACHE] 弱引用缓存命中: {cache_key}")
            #     return self.weak_cache[cache_key]

            # 3. 尝试Redis缓存（需要重建工具对象）
            if self.redis_client and tool_builder_func:
                try:
                    redis_key = f"mcp_tools:{cache_key}"
                    cached_metadata = self.redis_client.get(redis_key)

                    if cached_metadata:
                        metadata_list = json.loads(cached_metadata)
                        print(f"[CACHE] Redis缓存命中，开始重建工具: {cache_key}")

                        # 使用工具构建函数重建完整工具对象
                        rebuilt_tools = tool_builder_func(metadata_list, mcp_schema)

                        # 存入内存缓存
                        self.memory_cache[cache_key] = rebuilt_tools
                        self.memory_timestamps[cache_key] = current_time
                        # self.weak_cache[cache_key] = rebuilt_tools

                        self.stats['redis_hits'] += 1
                        self.stats['rebuilds'] += 1
                        return rebuilt_tools

                except (json.JSONDecodeError, redis.RedisError, Exception) as e:
                    print(f"[CACHE] Redis缓存读取失败: {e}")

            # 缓存未命中
            self.stats['misses'] += 1
            return None

    def set_cached_tools(self, mcp_schema: dict, tools: List[Any]):
        """设置缓存"""
        print("mcp_chema", mcp_schema)
        cache_key = self._get_cache_key(mcp_schema)
        current_time = time.time()

        with self.lock:
            # 存入内存缓存（完整对象）
            self.memory_cache[cache_key] = tools
            self.memory_timestamps[cache_key] = current_time
            # self.weak_cache[cache_key] = tools

            # 存入Redis缓存（仅元数据）
            if self.redis_client:
                try:
                    # 提取可序列化的元数据
                    metadata_list = []
                    for tool in tools:
                        if hasattr(tool, 'to_serializable_dict'):
                            metadata = tool.to_serializable_dict()
                        else:
                            metadata = {
                                'name': getattr(tool, 'name', ''),
                                'description': getattr(tool, 'description', ''),
                                'args_schema': getattr(tool, 'args_schema', {}),
                                'response_format': getattr(tool, 'response_format', 'content_and_artifact'),
                            }
                        metadata_list.append(metadata)

                    redis_key = f"mcp_tools:{cache_key}"
                    self.redis_client.setex(
                        redis_key,
                        self.redis_ttl,
                        json.dumps(metadata_list, ensure_ascii=False)
                    )
                    print(f"[CACHE] 已缓存到Redis: {cache_key}, 工具数量: {len(tools)}")

                except (json.JSONEncodeError, redis.RedisError) as e:
                    print(f"[CACHE] Redis缓存设置失败: {e}")

    def get_cache_stats(self) -> dict:
        """获取缓存统计"""
        with self.lock:
            total_requests = sum(self.stats.values())
            return {
                **self.stats,
                'total_requests': total_requests,
                'memory_hit_rate': self.stats['memory_hits'] / max(total_requests, 1) * 100,
                'redis_hit_rate': self.stats['redis_hits'] / max(total_requests, 1) * 100,
                'miss_rate': self.stats['misses'] / max(total_requests, 1) * 100,
                'memory_cache_size': len(self.memory_cache),

            }

    def clear_cache(self):
        """清空所有缓存"""
        with self.lock:
            self.memory_cache.clear()
            self.memory_timestamps.clear()

            if self.redis_client:
                try:
                    keys = self.redis_client.keys("mcp_tools:*")
                    if keys:
                        self.redis_client.delete(*keys)
                except redis.RedisError as e:
                    print(f"[CACHE] 清理Redis缓存失败: {e}")
