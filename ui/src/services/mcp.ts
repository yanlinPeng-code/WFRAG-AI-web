import {get,post} from '@/utils/request'

import {
  type CreateMcpToolProviderRequest,
  type GetMcpToolProviderResponse,
  type GetMcpToolProviderWithPageResponse,
  type GetMcpToolResponse,
  type UpdateMcpToolProviderRequest,
} from '@/models/mcp'
import type { BaseResponse } from '@/models/base'

// 获取mcp列表分页数据
export const getMcpToolProvidersWithPage = (
  current_page: number = 1,
  page_size: number = 20,
  search_word: string = '',
) =>{
  return get<GetMcpToolProviderWithPageResponse>('/mcp/mcp-tools',{
    params:{current_page,page_size,search_word},
  })


}



//校验mcp_schema

export const validateMcpSchema = (mcp_schema: string) =>{

  return post<BaseResponse<any>>('/mcp/validate-mcp-schema',{
    body:{mcp_schema},
  })


}


//创建mcp工具提供者

export const createMcpToolProvider = (req: CreateMcpToolProviderRequest) =>{
  return post<BaseResponse<any>>('/mcp/mcp-tools',{
    body:req,
  })
}

//更新mcp工具提供者详情
export const updateMcpToolProvider = (provider_id: string, req: UpdateMcpToolProviderRequest) =>{
  return post<BaseResponse<any>>(`/mcp/mcp-tools/${provider_id}`,{
    body:req,
  })
}

//删除mcp工具提供者信息
export const deleteMcpToolProvider = (provider_id: string) =>{
  return  post<BaseResponse<any>>(`/mcp/mcp-tools/${provider_id}/delete`,{
  })

}

//获取mcp工具提供者详情
export const getMcpToolProvider = (provider_id: string) =>{
  return get<GetMcpToolProviderResponse>(`/mcp/mcp-tools/${provider_id}`)
}

//获取mcp工具详情
export const getMcpTool = (provider_id: string,tool_name: string) =>{
  return get<GetMcpToolResponse>(`/mcp/mcp-tools/${provider_id}/tools/${tool_name}`)
}
