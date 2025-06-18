from uuid import UUID

from celery import shared_task


@shared_task
def handle_mcp_tool(
        account_id: UUID,
        mcp_provider_id: UUID,
        real_mcp_schema: dict
):
    from app.http.module import injector
    from internal.service.mcp_service import McpService
    mcp_service = injector.get(McpService)
    mcp_service.handle_mcp_tool(
        account_id=account_id,
        mcp_provider_id=mcp_provider_id,
        real_mcp_schema=real_mcp_schema
    )


@shared_task
def update_mcp_tool(
        account_id: UUID,
        mcp_provider_id: UUID,
        real_mcp_schema: dict,
):
    from app.http.module import injector
    from internal.service.mcp_service import McpService
    mcp_service = injector.get(McpService)
    mcp_service.update_mcp_tool(account_id=account_id,
                                mcp_provider_id=mcp_provider_id,
                                real_mcp_schema=real_mcp_schema
                                )
