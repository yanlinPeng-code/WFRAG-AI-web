import { get, post, ssePost } from '@/utils/request'
import type {
  CreateWorkflowRequest,
  GetDraftGraphResponse,
  GetWorkflowResponse,
  GetWorkflowsWithPageRequest,
  GetWorkflowsWithPageResponse,
  UpdateDraftGraphRequest,
  UpdateWorkflowRequest,
} from '@/models/workflow'
import type { BaseResponse } from '@/models/base'

// 获取工作流分页列表数据
export const getWorkflowsWithPage = (req: GetWorkflowsWithPageRequest) => {
  return get<GetWorkflowsWithPageResponse>(`/workflows`, { params: req })
}

// 在当前账号下新增工作流
export const createWorkflow = (req: CreateWorkflowRequest) => {
  return post<BaseResponse<{ id: string }>>(`/workflows`, { body: req })
}

// 修改工作流基础信息
export const updateWorkflow = (workflow_id: string, req: UpdateWorkflowRequest) => {
  return post<BaseResponse<any>>(`/workflows/${workflow_id}`, { body: req })
}

// 获取工作流基础信息
export const getWorkflow = (workflow_id: string) => {
  return get<GetWorkflowResponse>(`/workflows/${workflow_id}`)
}

// 删除指定的工作流
export const deleteWorkflow = (workflow_id: string) => {
  return post<BaseResponse<any>>(`/workflows/${workflow_id}/delete`)
}

// 获取指定工作流的graph图草稿配置
export const getDraftGraph = (workflow_id: string) => {
  return get<GetDraftGraphResponse>(`/workflows/${workflow_id}/draft-graph`)
}

// 更新指定工作流的graph图草稿配置
export const updateDraftGraph = (workflow_id: string, req: UpdateDraftGraphRequest) => {
  return post<BaseResponse<any>>(`/workflows/${workflow_id}/draft-graph`, { body: req })
}

// 发布指定的工作流
export const publishWorkflow = (workflow_id: string) => {
  return post<BaseResponse<any>>(`/workflows/${workflow_id}/publish`)
}

// 取消发布指定的工作流
export const cancelPublishWorkflow = (workflow_id: string) => {
  return post<BaseResponse<any>>(`/workflows/${workflow_id}/cancel-publish`)
}

// 工作流调试，该接口为流式事件输出
export const debugWorkflow = (
  workflow_id: string,
  inputs: Record<string, any>,
  onData: (event_response: Record<string, any>) => void,
) => {
  return ssePost(`/workflows/${workflow_id}/debug`, { body: inputs }, onData)
}
