// api请求接口前缀
export const apiPrefix: string = "http://43.136.71.179/api"


// 业务状态码
export const httpCode = {
  success: 'success',
  fail: 'fail',
  notFound: 'not_found',
  unauthorized: 'unauthorized',
  forbidden: 'forbidden',
  validateError: 'validate_error',
}

// 类型字符串与中文映射
export const typeMap: { [key: string]: string } = {
  str: '字符串',
  int: '整型',
  float: '浮点型',
  bool: '布尔值',
}

// 智能体事件类型
export const QueueEvent = {
  longTermMemoryRecall: 'QueueEvent.LONG_TERM_MEMORY_RECALL',
  agentThought: 'QueueEvent.AGENT_THOUGHT',
  agentMessage: 'QueueEvent.AGENT_MESSAGE',
  agentAction: 'QueueEvent.AGENT_ACTION',
  datasetRetrieval: 'QueueEvent.DATASET_RETRIEVAL',
  agentEnd: 'QueueEvent.AGENT_END',
  stop: 'QueueEvent.STOP',
  error: 'QueueEvent.ERROR',
  timeout: 'QueueEvent.TIMEOUT',
  ping: 'QueueEvent.PING',
}
export const QueueEVENT= {
  longTermMemoryRecall: 'long_term_memory_recall',
  agentThought: 'agent_thought',
  agentMessage: 'agent_message',
  agentAction: 'agent_action',
  datasetRetrieval: 'dataset_retrieval',
  agentEnd: 'agent_end',
  stop: 'stop',
  error: 'error',
  timeout: 'timeout',
  ping: 'ping',
}
// export const QueueEvent = {
//    longTermMemoryRecall: 'long_term_memory_recall',
//   agentThought: 'agent_thought',
//   agentMessage: 'agent_message',
//   agentAction: 'agent_action',
//   datasetRetrieval: 'dataset_retrieval',
//   agentEnd: 'agent_end',
//   stop: 'stop',
//   error: 'error',
//   timeout: 'timeout',
//   ping: 'ping',
// }
// export const QueueEVENT={
//   longTermMemoryRecall: 'long_term_memory_recall',
//   agentThought: 'agent_thought',
//   agentMessage: 'agent_message',
//   agentAction: 'agent_action',
//   datasetRetrieval: 'dataset_retrieval',
//   agentEnd: 'agent_end',
//   stop: 'stop',
//   error: 'error',
//   timeout: 'timeout',
//   ping: 'ping',
//
//
// }