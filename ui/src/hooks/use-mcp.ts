import {ref} from 'vue'

import {
  createMcpToolProvider,
  deleteMcpToolProvider,
  getMcpTool,
  getMcpToolProvider,
  getMcpToolProvidersWithPage,
  updateMcpToolProvider,
  validateMcpSchema,
} from '@/services/mcp'

import {Message,Modal} from '@arco-design/web-vue'
import type  {CreateMcpToolProviderRequest,UpdateMcpToolProviderRequest} from '@/models/mcp'



export const useGetMcpToolProvider=()=>{
  //定义hooks所需数据
  const loading=ref(false)
  const mcp_tool_provider=ref<Record<string,any>>({})

  // 2.定义加载数据函数
  const loadMcpToolProvider=async(provider_id:string)=>{

    try {
      loading.value=true
      const resp=await getMcpToolProvider(provider_id)
      mcp_tool_provider.value=resp.data


    }finally {
      loading.value=false
    }

  }
  return {loading,mcp_tool_provider,loadMcpToolProvider}

}
// use-mcp.ts or wherever your hook is defined




export const useGetMcpTool=()=>{

  //定义hooks所需数据
  const loading=ref(false)
  const mcp_tool=ref<Record<string,any>>({})


  //  2.定义加载数据函数
  const loadMcpTool=async(provider_id:string,tool_name:string)=>{
    try {
      loading.value=true
      const resp=await getMcpTool(provider_id,tool_name)
      mcp_tool.value=resp.data
    }finally {
      loading.value=false
    }


  }
  return {loading,mcp_tool,loadMcpTool}

}



export const useGetMcpToolProvidersWithPage = () => {
  // 1.定义hooks所需数据
  const loading = ref(false)
  const mcp_tool_providers = ref<Record<string, any>>([])
  const defaultPaginator = {
    current_page: 1,
    page_size: 20,
    total_page: 0,
    total_record: 0,
  }
  const paginator = ref(defaultPaginator)

  // 2.定义加载数据函数
  const loadMcpToolProviders = async (
    init: boolean = false,
    search_word: string = '') => {
    // 2.1 判断是否是初始化，如果是的话则先初始化分页器
    if (init) {
      paginator.value = defaultPaginator
      Object.assign(paginator, { ...defaultPaginator })
    } else if (paginator.value.current_page > paginator.value.total_page) {
      return
    }

    // 2.2 加载更多数据并更新数据状态
    try {
      // 2.3 调用接口获取响应数据
      loading.value = true
      const resp = await getMcpToolProvidersWithPage(
        paginator.value.current_page,
        paginator.value.page_size,
        search_word,
      )
      const data = resp.data

      // 2.4 更新分页器
      paginator.value = data.paginator

      // 2.5 判断是否存在更多数据
      if (paginator.value.current_page <= paginator.value.total_page) {
        paginator.value.current_page += 1
      }

      // 2.6 追加或者是覆盖数据
      if (init) {
        mcp_tool_providers.value = data.list
      } else {
        mcp_tool_providers.value.push(...data.list)
      }
    } finally {
      loading.value = false
    }
  }

  return { loading, mcp_tool_providers, paginator, loadMcpToolProviders }
}


export const useDeleteMcpToolProvider = () => {

  const handleDelete=(provider_id:string,success_callback?:()=>void)=>{
    Modal.warning({
      title:'删除这个工具?',
      content:'删除工具是不可逆的。AI应用将无法再访问您的工具',
      hideCancel:false,
      onOk:async()=>{
        try{
          const resp=await deleteMcpToolProvider(provider_id)
          Message.success(resp.message)
        }finally{
          success_callback&&success_callback()
        }
      },
    })
  }
  return {handleDelete}
}
export const useUpdateMcpToolProvider = () => {
  //  定义hooks所需数据
  const loading=ref(false)
  const handleUpdateMcpToolProvider=async(provider_id:string,req:UpdateMcpToolProviderRequest)=>{
    try {
      loading.value=true
      const resp=await updateMcpToolProvider(provider_id,req)
      Message.success(resp.message)
    }finally {
      loading.value=false
    }

  }
  return {loading,handleUpdateMcpToolProvider}
}

export const useCreateMcpToolProvider = () => {
  //  定义hooks所需数据
  const loading=ref(false)
  const handleCreateMcpToolProvider=async(req:CreateMcpToolProviderRequest)=>{
    try {
      loading.value=true
      const resp=await createMcpToolProvider(req)
      Message.success(resp.message)
    }finally {
      loading.value=false
    }

  }
  return {loading,handleCreateMcpToolProvider}
}

export const useValidateMcpSchema = () => {
  //  定义hooks所需数据
  const loading=ref(false)
  const handleValidateMcpSchema=async(mcp_schema:string)=>{
    try {
      loading.value=true
      const resp=await validateMcpSchema(mcp_schema)
      Message.success(resp.message)
    }finally {
      loading.value=false
    }

  }
  return {loading,handleValidateMcpSchema}
}
