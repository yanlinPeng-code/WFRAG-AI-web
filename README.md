# WFRAG-AI-web  原生 AI 应用开发平台项目文档

## 一、项目概述
本项目是一个智能应用系统，基于 langchain/langgraph 框架，结合 mcp（模型上下文协议）构建而成。该平台提供了一系列核心模块，涵盖工作流编排、大语言模型配置、应用发布与编辑、可视化统计以及多种插件功能，为开发者提供了一站式的 AI 应用开发与管理解决方案。

## 二、核心模块
1. **工作流模块**：借助 langgraph 框架，实现可视化编排工作流功能，方便开发者灵活设计和调整业务流程。
2. **大语言配置**：基于 langchain 框架，支持大语言模型的配置，可根据不同需求选择和定制合适的模型。
3. **应用发布模块**：提供应用发布功能，将开发好的应用部署到生产环境。
4. **应用编辑模块**：允许开发者对已有的应用进行编辑和修改，满足不断变化的业务需求。
5. **可视化统计模块**：提供可视化统计功能，帮助开发者直观地了解应用的运行情况和性能指标。
6. **内置插件模块**：提供内置插件功能，增强系统的扩展性和功能性。
7. **mcp 插件模块**：支持 mcp 插件，实现与外部系统的高效集成。
8. **在线 api 插件模块**：提供在线 api 插件功能，方便开发者调用外部服务。
9. **agent 模块**：提供 agent 功能，包含 sql 代理、工具代理和大语言代理，提升系统的智能化水平。

## 三、项目结构
```
.gitignore
README.md
docker/
  docker-compose.drawio
  docker-compose.jpg
  docker-compose.svg
  docker-compose.yaml
  nginx/
  postgres/
ui/
  ...
api/
  .env.example
  .gitattributes
  .gitignore
  Dockerfile
  Dockerfile-unstructured
  README.md
  app/
  config/
  docker/
  internal/
  pkg/
  pytest.ini
  requirements-dev.in
  requirements-dev.txt
  requirements.in
  requirements.txt
  test/
```

## 四、UI 项目设置与运行
### 1. 安装依赖
```sh
yarn
```

### 2. 开发环境启动
```sh
yarn dev
```

### 3. 生产环境构建
```sh
yarn build
```

### 4. 运行单元测试
```sh
yarn test:unit
```

### 5. 代码检查
```sh
yarn lint
```

## 五、API 项目设置与运行
### 1. 配置环境变量
复制 `.env.example` 文件为 `.env`，并根据实际情况修改其中的配置项。

### 2. 数据库迁移（如果需要）
在 `docker-compose.yaml` 中，`MIGRATION_ENABLED` 设置为 `true` 时，容器启动会自动进行数据库迁移。

### 3. 使用 Docker 部署
确保已经安装 Docker 和 Docker Compose，然后在项目根目录下执行以下命令：
```sh
docker-compose up -d
```

## 六、docker-compose.yaml 配置说明
`docker-compose.yaml` 文件用于定义和运行多容器 Docker 应用程序。以下是对该文件中各个服务的详细说明：

```yaml
version: '3'
services:
  llmops-ui:
    image: llmops-ui:0.1.0
    build:
      context: ../ui
      dockerfile: Dockerfile
    container_name: llmops-ui
    restart: always
    environment: [ ]
    ports:
      - "3000:3000"
```
- **llmops-ui**：前端用户界面服务。
  - **镜像**：`llmops-ui:0.1.0`
  - **构建上下文**：`../ui` 目录
  - **Dockerfile**：`Dockerfile`
  - **端口映射**：将容器的 3000 端口映射到主机的 3000 端口

```yaml
  llmops-api:
    image: llmops-api:0.1.0
    build:
      context: ../api
      dockerfile: Dockerfile
    container_name: llmops-api
    restart: always
    volumes:
      - ./volumes/app/storage:/app/api/storage
    environment:
      # 模式为API，代表启用API服务
      MODE: api
      SERVER_WORKER_AMOUNT: 4
      SERVER_THREAD_AMOUNT: 4
      # 数据库迁移配置
      MIGRATION_ENABLED: 'true'
      # JWT加密秘钥
      JWT_SECRET_KEY:
      # 服务配置 - 修改为您的IP地址
      SERVICE_IP: 
      SERVICE_API_PREFIX: 
      # CSRF校验开关
      WTF_CSRF_ENABLED: 'false'
      # SQLAlchemy数据库配置
      SQLALCHEMY_DATABASE_URI: postgresql://postgres:llmops123456@llmops-db:5432/llmops?client_encoding=utf8
      SQLALCHEMY_POOL_SIZE: 30
      SQLALCHEMY_POOL_RECYCLE: 3600
      SQLALCHEMY_ECHO: 'true'
      # Redis缓存数据库配置
      REDIS_HOST: llmops-redis
      REDIS_PORT: 6379
      REDIS_USERNAME: ''
      REDIS_PASSWORD: ''
      REDIS_DB: 0
      REDIS_USE_SSL: 'false'
      # Weaviate向量数据库配置
      WEAVIATE_HTTP_HOST: llmops-weaviate
      WEAVIATE_HTTP_PORT: 8080
      WEAVIATE_GRPC_HOST: llmops-weaviate
      WEAVIATE_GRPC_PORT: 50051
      WEAVIATE_API_KEY: ftBC9hKkjfdbdi0wW3T6kEtMh5BZFpGa1DF8
      # 腾讯云COS对象存储
      COS_SECRET_ID: 
      COS_SECRET_KEY: 
      COS_REGION: 
      COS_SCHEME: 
      COS_BUCKET: 
      COS_DOMAIN: 
      # Celery异步队列任务配置
      CELERY_BROKER_DB: 1
      CELERY_RESULT_BACKEND_DB: 1
      CELERY_TASK_IGNORE_RESULT: 'true'
      CELERY_RESULT_EXPIRES: 3600
      CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP: 'true'
      # Github OAuth应用秘钥 - 由于无法使用域名，这些配置可能需要调整
      GITHUB_CLIENT_ID:
      GITHUB_CLIENT_SECRET: 
      GITHUB_REDIRECT_URI: 
      # LangSmith配置
      LANGSMITH_TRACING: 'true'
      LANGSMITH_ENDPOINT: https://api.smith.langchain.com
      LANGSMITH_API_KEY: 
      LANGSMITH_PROJECT:
      # HuggingFace配置
      TRANSFORMERS_OFFLINE: 0
      # 辅助Agent智能体应用id标识
      ASSISTANT_AGENT_ID: f47ac10b-58cc-4372-a567-0e02b2c3d479
      # OpenAI服务提供者
      OPENAI_API_KEY:
      OPENAI_BASE_URL: 
      # DeepSeek服务提供者
      DEEPSEEK_API_KEY: 
      DEEPSEEK_API_BASE:
      # 百度千帆服务提供者
      qianfan_ak: 
      qianfan_sk: 
      # 月之暗面服务提供者
      MOONSHOT_API_KEY: 
      # 通义千问服务提供者
      DASHSCOPE_API_KEY: 
      DASHSCOPE_BASE_URL: 
      # 高德工具API秘钥
      GAODE_API_KEY: 
      # 谷歌Serper搜索API秘钥
      SERPER_API_KEY:
    ports:
      - "5001:5001"
    depends_on:
      - llmops-db
      - llmops-redis
      - llmops-weaviate
```
- **llmops-api**：后端 API 服务。
  - **镜像**：`llmops-api:0.1.0`
  - **构建上下文**：`../api` 目录
  - **Dockerfile**：`Dockerfile`
  - **数据卷挂载**：将主机的 `./volumes/app/storage` 目录挂载到容器的 `/app/api/storage` 目录
  - **环境变量**：包含服务模式、数据库配置、缓存配置、第三方服务配置等
  - **端口映射**：将容器的 5001 端口映射到主机的 5001 端口
  - **依赖服务**：依赖于 `llmops-db`、`llmops-redis` 和 `llmops-weaviate`

```yaml
  llmops-celery:
    image: llmops-api:0.1.0
    build:
      context: ../api
      dockerfile: Dockerfile
    container_name: llmops-celery
    restart: always
    volumes:
      - ./volumes/app/storage:/app/api/storage
    environment:
      # 模式为celery，代表启用Celery异步任务队列
      MODE: celery
      CELERY_WORKER_AMOUNT: 4
      # 数据库迁移配置
      MIGRATION_ENABLED: 'false'
      # 服务配置 - 修改为您的IP地址
      SERVICE_IP: 
      SERVICE_API_PREFIX: 
      # JWT加密秘钥
      JWT_SECRET_KEY: 
      # CSRF校验开关
      WTF_CSRF_ENABLED: 'false'
      # SQLAlchemy数据库配置
      SQLALCHEMY_DATABASE_URI: postgresql://postgres:llmops123456@llmops-db:5432/llmops?client_encoding=utf8
      SQLALCHEMY_POOL_SIZE: 30
      SQLALCHEMY_POOL_RECYCLE: 3600
      SQLALCHEMY_ECHO: 'true'
      # Redis缓存数据库配置
      REDIS_HOST: llmops-redis
      REDIS_PORT: 6379
      REDIS_USERNAME: ''
      REDIS_PASSWORD: ''
      REDIS_DB: 0
      REDIS_USE_SSL: 'false'
      # Weaviate向量数据库配置
      WEAVIATE_HTTP_HOST: llmops-weaviate
      WEAVIATE_HTTP_PORT: 8080
      WEAVIATE_GRPC_HOST: llmops-weaviate
      WEAVIATE_GRPC_PORT: 50051
      WEAVIATE_API_KEY: ftBC9hKkjfdbdi0wW3T6kEtMh5BZFpGa1DF8
      # 腾讯云COS对象存储
      COS_SECRET_ID: 
      COS_SECRET_KEY: 
      COS_REGION: 
      COS_SCHEME: 
      COS_BUCKET: 
      COS_DOMAIN: 
      # Celery异步队列任务配置
      CELERY_BROKER_DB: 1
      CELERY_RESULT_BACKEND_DB: 1
      CELERY_TASK_IGNORE_RESULT: 'true'
      CELERY_RESULT_EXPIRES: 3600
      CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP: 'true'
      # Github OAuth应用秘钥 - 由于无法使用域名，这些配置可能需要调整
      GITHUB_CLIENT_ID: 
      GITHUB_CLIENT_SECRET: 
      GITHUB_REDIRECT_URI: 
      # LangSmith配置
      LANGSMITH_TRACING:  'true'
      LANGSMITH_ENDPOINT:  https://api.smith.langchain.com
      LANGSMITH_API_KEY: 
      LANGSMITH_PROJECT:
      # HuggingFace配置
      TRANSFORMERS_OFFLINE: 0
      # 辅助Agent智能体应用id标识
      ASSISTANT_AGENT_ID: f47ac10b-58cc-4372-a567-0e02b2c3d479
      # OpenAI服务提供者
      OPENAI_API_KEY: 
      OPENAI_API_BASE: 
      # DeepSeek服务提供者
      DEEPSEEK_API_KEY: 
      DEEPSEEK_API_BASE:
      # 百度千帆服务提供者
      qianfan_ak: 
      qianfan_sk: 
      # 月之暗面服务提供者
      MOONSHOT_API_KEY: 
      # 通义千问服务提供者
      DASHSCOPE_API_KEY: 
      DASHSCOPE_API_BASE:
      # 高德工具API秘钥
      GAODE_API_KEY: 
      # 谷歌Serper搜索API秘钥
      SERPER_API_KEY: 
    depends_on:
      - llmops-db
      - llmops-redis
      - llmops-weaviate
```
- **llmops-celery**：Celery 异步任务队列服务。
  - **镜像**：`llmops-api:0.1.0`
  - **构建上下文**：`../api` 目录
  - **Dockerfile**：`Dockerfile`
  - **数据卷挂载**：将主机的 `./volumes/app/storage` 目录挂载到容器的 `/app/api/storage` 目录
  - **环境变量**：包含服务模式、数据库配置、缓存配置、第三方服务配置等
  - **依赖服务**：依赖于 `llmops-db`、`llmops-redis` 和 `llmops-weaviate`

```yaml
  llmops-redis:
    image: redis:6-alpine
    restart: always
    container_name: llmops-redis
    volumes:
      - ./volumes/redis/data:/data
    # 启动redis服务时配置
    command: redis-server 
    healthcheck:
      test: [ "CMD", "redis-cli", "ping" ]
    ports:
      - "6379:6379"
```
- **llmops-redis**：Redis 缓存数据库服务。
  - **镜像**：`redis:6-alpine`
  - **数据卷挂载**：将主机的 `./volumes/redis/data` 目录挂载到容器的 `/data` 目录
  - **启动命令**：`redis-server`
  - **健康检查**：使用 `redis-cli ping` 命令检查 Redis 服务是否正常运行
  - **端口映射**：将容器的 6379 端口映射到主机的 6379 端口

```yaml
  llmops-db:
    image: postgres:15-alpine
    restart: always
    container_name: llmops-db
    environment:
      # 配置默认的账户名、账户密码、默认数据库、数据存储的位置
      PGUSER: postgres
      POSTGRES_PASSWORD: llmops123456
      POSTGRES_DB: llmops
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      # 将postgres数据挂载到本地./volumes/db/data上
      - ./volumes/db/data:/var/lib/postgresql/data/pgdata
      # 初始化脚本只有在空数据挂载的情况下才会触发执行(.sql/.sh等)，如果已经存在数据则不会执行
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      # 每隔1s发起一个健康测试，最多重试30次
      test: [ "CMD", "pg_isready" ]
      interval: 1s
      timeout: 3s
      retries: 30
    ports:
      - "5432:5432"
```
- **llmops-db**：PostgreSQL 数据库服务。
  - **镜像**：`postgres:15-alpine`
  - **环境变量**：包含数据库用户名、密码、数据库名和数据存储位置
  - **数据卷挂载**：将主机的 `./volumes/db/data` 目录挂载到容器的 `/var/lib/postgresql/data/pgdata` 目录，将 `./postgres/init.sql` 脚本挂载到容器的 `/docker-entrypoint-initdb.d/init.sql` 目录
  - **健康检查**：使用 `pg_isready` 命令检查 PostgreSQL 服务是否正常运行
  - **端口映射**：将容器的 5432 端口映射到主机的 5432 端口

```yaml
  llmops-weaviate:
    image: semitechnologies/weaviate:1.28.4
    container_name: llmops-weaviate
    restart: always
    environment:
      QUERY_DEFAULTS_LIMIT: 25  # 查询默认返回的数据条数
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'false'  # 需要授权才能和weaviate进行交互
      PERSISTENCE_DATA_PATH: /var/lib/weaviate  # weaviate数据存储路径
      DEFAULT_VECTORIZER_MODULE: 'none'  # 向量化模块设置为none
      CLUSTER_HOSTNAME: 'node1'  # 节点的主机名字
      AUTHENTICATION_APIKEY_ENABLED: 'true'  # 启动基于API秘钥的身份校验
      AUTHENTICATION_APIKEY_ALLOWED_KEYS: 'ftBC9hKkjfdbdi0wW3T6kEtMh5BZFpGa1DF8'  # 允许的API秘钥列表
      AUTHENTICATION_APIKEY_USERS: 'llmops@peng.com'  # 基于秘钥的API身份列表
      AUTHORIZATION_ADMINLIST_ENABLED: 'true'  # 启动AdminList授权方案
      AUTHORIZATION_ADMINLIST_USERS: 'llmops@peng.com'  # 使用AdminList方案时具有管理权限的用户
    volumes:
      - ./volumes/weaviate:/var/lib/weaviate
    ports:
      - "8080:8080"
      - "50051:50051"
```
- **llmops-weaviate**：Weaviate 向量数据库服务。
  - **镜像**：`semitechnologies/weaviate:1.28.4`
  - **环境变量**：包含查询配置、身份验证配置、数据存储路径等
  - **数据卷挂载**：将主机的 `./volumes/weaviate` 目录挂载到容器的 `/var/lib/weaviate` 目录
  - **端口映射**：将容器的 8080 端口和 50051 端口分别映射到主机的 8080 端口和 50051 端口

```yaml
  llmops-nginx:
    image: nginx:latest
    restart: always
    container_name: llmops-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/proxy.conf:/etc/nginx/proxy.conf
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/ssl
    depends_on:
      - llmops-ui
      - llmops-api
    ports:
      - "80:80"
      - "443:443"
```
- **llmops-nginx**：Nginx 反向代理服务。
  - **镜像**：`nginx:latest`
  - **数据卷挂载**：将主机的 `./nginx/nginx.conf`、`./nginx/proxy.conf`、`./nginx/conf.d` 和 `./nginx/ssl` 目录分别挂载到容器的 `/etc/nginx/nginx.conf`、`/etc/nginx/proxy.conf`、`/etc/nginx/conf.d` 和 `/etc/ssl` 目录
  - **依赖服务**：依赖于 `llmops-ui` 和 `llmops-api`
  - **端口映射**：将容器的 80 端口和 443 端口分别映射到主机的 80 端口和 443 端口

## 七、注意事项
- 在部署前，请确保已经正确配置了所有的环境变量，特别是数据库连接信息、API 密钥等。

- 如果需要修改服务的配置参数，可以直接在 `docker-compose.yaml` 文件中进行调整。

- 由于该项目是同步适配项目，对于mcp服务，作者占时没有想到适配异步工具的方法。

- 如果要适配mcp服务，请你修改langchain_mcp_adapter的源码，这里有简单的例子,这是笔者的拙劣见解，还希望大佬能够找到一种更好的方法。我也会多多学习，另外，当部署时，mcp功能会受限。

  在 StructuredTool包中加入以下

  ```python
  def _run(
        self,
        *args: Any,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> Any:
        """Use the tool."""
        if self.func:
            if run_manager and signature(self.func).parameters.get("callbacks"):
                kwargs["callbacks"] = run_manager.get_child()
            if config_param := _get_runnable_config_param(self.func):
                kwargs[config_param] = config
            return self.func(*args, **kwargs)
        msg = "StructuredTool does not support sync invocation."
        raise NotImplementedError(msg)
  ```

  在langchain_mcp_adapters 的  tools中修改以下代码

  

      async def load_mcp_tools(
          session: ClientSession | None,
          *,
          connection: Connection | None = None,
      ) -> list[BaseTool]:
          """Load all available MCP tools and convert them to LangChain tools.
      
          Returns:
              list of LangChain tools. Tool annotations are returned as part
              of the tool metadata object.
          """
          if session is None and connection is None:
              raise ValueError("Either a session or a connection config must be provided")
          
          if session is None:
              # If a session is not provided, we will create one on the fly
              async with create_session(connection) as tool_session:
                  await tool_session.initialize()
                  tools = await tool_session.list_tools()
          else:
              tools = await session.list_tools()
          
          converted_tools = [
              convert_mcp_tool_to_langchain_tool_sync(session, tool, connection=connection)
              for tool in tools.tools
          ]
          return converted_tools

  

  ```python
  def convert_mcp_tool_to_langchain_tool_sync(
      session: ClientSession | None,
      tool: MCPTool,
      *,
      connection: Connection | None = None,
  ) -> BaseTool:
      """Convert an MCP tool to a LangChain tool in a synchronous manner.
      NOTE: This tool runs MCP operations by blocking the current thread using `asyncio.run()`.
        It should NOT be called from within an already running asyncio event loop,
        as this will raise a `RuntimeError`.
  
  Args:
      session: An existing MCP client session. If provided, `connection` is ignored.
      tool: The MCP tool to convert.
      connection: Optional connection configuration to use to create a new session
                  if a `session` is not provided.
  
  Returns:
      A LangChain `BaseTool` that can be called synchronously.
  """
  if session is None and connection is None:
      raise ValueError("Either a session or a connection config must be provided")
  
  # Modified call_tool_sync to accept arguments more flexibly
  def call_tool_sync(
      *args: Any, # Accept positional arguments
      callbacks: Optional[CallbackManagerForToolRun] = None, # LangChain might pass this
      config: Optional[RunnableConfig] = None, # LangChain might pass this
      **kwargs: Any, # Accept keyword arguments
  ) -> Tuple[str | List[str], List[NonTextContent] | None]:
      """
      Synchronous wrapper for the asynchronous MCP tool call.
      This function uses asyncio.run() to execute the underlying async logic.
      It is designed to handle arguments passed by LangChain's Tool.run method.
      """
      arguments: dict[str, Any] = {}
  
      # If LangChain passes a single positional argument, assume it's the main input
      if args:
          # If args_schema has a single top-level key like 'query', it might be passed directly
          # If the schema implies a dict, LangChain might pass a dict as the single arg
          if len(args) == 1 and isinstance(args[0], dict):
              arguments = args[0]
          elif len(tool.inputSchema.get("properties", {})) == 1 and "type" in tool.inputSchema and tool.inputSchema["type"] == "object":
              # If the schema is a single-property object, try to map the positional arg
              single_prop_name = list(tool.inputSchema["properties"].keys())[0]
              arguments[single_prop_name] = args[0]
          else:
              # Fallback: Treat positional args as values if the schema is simpler or if it's the expected way
              # This part might need fine-tuning based on your exact MCPTool inputSchema
              # For now, let's assume if it's a single arg, it's the primary input.
              # If it's a dict, it's already structured.
              arguments = {"input": args[0]} if len(args) == 1 else {"args_list": list(args)} # Example handling
              # A more robust approach might parse args based on tool.inputSchema
              print(f"Warning: Positional arguments provided. Attempting to convert: {args}")
  
      # Merge with keyword arguments
      arguments.update(kwargs)
  
      async def _run_async_call():
          """The actual asynchronous logic to be executed."""
          if session is None:
              # If a session is not provided, create one on the fly.
              async with create_session(connection) as tool_session:
                  call_tool_result = await cast(ClientSession, tool_session).call_tool(
                      tool.name, arguments
                  )
          else:
              # Use the provided session.
              call_tool_result = await session.call_tool(tool.name, arguments)
          return _convert_call_tool_result(call_tool_result)
  
      # Execute the asynchronous logic synchronously, blocking the current thread.
      return asyncio.run(_run_async_call())
  
  # Create a LangChain StructuredTool with the synchronous `func` attribute.
  return StructuredTool(
      name=tool.name,
      description=tool.description or "",
      args_schema=tool.inputSchema,
      func=call_tool_sync,  # Use 'func' for synchronous tools
      response_format="content_and_artifact",
      metadata=tool.annotations.model_dump() if tool.annotations else None,
  )
  ```

- 确保服务器上的端口没有被其他服务占用，避免启动失败。

通过以上步骤，你可以顺利部署和运行 WFRAG-AI-web 原生 AI 应用开发平台项目。
