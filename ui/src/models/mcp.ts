import {type BasePaginatorResponse,type BaseResponse} from '@/models/base'


//获取mcpAPI插件相应接口

export  type GetMcpToolProviderWithPageResponse=BasePaginatorResponse<{
  id:  string
  name: string
  icon: string
  description: string
  headers: Array<any>
  tools: Array<any>
  created_at: number



}>

//新增mcpAPI插件提供者请求接口
export type CreateMcpToolProviderRequest={

  name:  string
  icon:  string
  mcp_schema:  string
  headers:  Array<any>

}

// 更新mcp工具提供者请求与响应结构
export type UpdateMcpToolProviderRequest={

  name:  string
  icon:  string
  mcp_schema:  string
  headers:  Array<any>

}

//获取mcp工具提供者响应结构体

export type GetMcpToolProviderResponse=BaseResponse<{
  id:  string
  name:  string
  icon:  string
  description:  string
  headers:  Array<any>
  mcp_schema:  string
  created_at:  number


}>
// 获取mcpAPI工具详情
export type GetMcpToolResponse=BaseResponse<{
  id:  string
  name:  string
  description:  string
  provider:  {
    id:  string
    name:  string

    icon:  string
    headers:  {
      key:  string
      value:  string
    }[]
    description:  string
  }
  inputs:  {
    type:  string
    name:  string
    required:  boolean
    description:  string
  }[]
  
}>



