

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  useCreateMcpToolProvider,
  useDeleteMcpToolProvider,
  useGetMcpToolProvider,
  useGetMcpToolProvidersWithPage,
  useUpdateMcpToolProvider,
  useValidateMcpSchema,
} from '@/hooks/use-mcp'
import { useUploadImage } from '@/hooks/use-upload-file'
import { type CreateMcpToolProviderRequest } from '@/models/mcp'
import moment from 'moment/moment'
import { typeMap } from '@/config'
import { type FileItem, Form, type ValidatedError } from '@arco-design/web-vue'

// 1.定义额面所需数据
const route = useRoute()
const props = defineProps({
  createType: { type: String, required: true },
})
const emits = defineEmits(['update:create-type'])
const form = ref<{
  fileList: FileItem[]
  icon: string
  description: string
  name: string
  mcp_schema: string
  headers: Record<string, any>[]
}>({
  fileList: [],
  icon: '',
  description: '',
  name: '',
  mcp_schema: '',
  headers: [],
})
const { image_url, handleUploadImage } = useUploadImage()
const {
  loading: getMcpToolProviderLoading,
  mcp_tool_provider,
  loadMcpToolProvider,
} = useGetMcpToolProvider()
const {
  loading: getMcpToolProvidersLoading,
  paginator,
  mcp_tool_providers,
  loadMcpToolProviders,
} = useGetMcpToolProvidersWithPage()
const { handleDelete: handleDeleteMcpToolProvider } = useDeleteMcpToolProvider()
const {
  loading: updateMcpToolProviderLoading,
  handleUpdateMcpToolProvider, //
} = useUpdateMcpToolProvider()
const {
  loading: createMcpToolProviderLoading,
  handleCreateMcpToolProvider, //
} = useCreateMcpToolProvider()
const { handleValidateMcpSchema } = useValidateMcpSchema()
const formRef = ref<InstanceType<typeof Form>>()
const showIdx = ref<number>(-1)
const loading = ref<boolean>(false)
const showUpdateModal = ref<boolean>(false)
const tools = computed(() => {
// First, check if showIdx is valid and if mcp_tool_providers has data
  if (showIdx.value === -1 || !mcp_tool_providers.value || mcp_tool_providers.value.length === 0) {
    return []; // Return an empty array if no provider is selected or data is not loaded
  }

// Get the currently selected provider based on showIdx
// This assumes showIdx correctly corresponds to an index in mcp_tool_providers.value
  const selectedProvider = mcp_tool_providers.value[showIdx.value];

// If for some reason the selected provider is not found or is invalid
  if (!selectedProvider || !Array.isArray(selectedProvider.tools)) {
    console.warn("Selected provider or its tools array is invalid:", selectedProvider);
    return [];
  }

// Map the tools of the selected provider to the desired format
  return selectedProvider.tools.map((tool: any) => {
    return {
      id: tool.id,
      name: tool.name,
      description: tool.description,
// You might not need the 'provider' object here if you're only showing tools
// for a *single* selected provider, as the context is already that provider.
// However, if you want to include it for consistency with other parts of your app, keep it.
      provider: {
        id: selectedProvider.id,
        name: selectedProvider.name,
        icon: selectedProvider.icon,
        label: selectedProvider.label,
        description: selectedProvider.description,
      },
      inputs: tool.inputs || [],
      method: tool.method || null,
      path: tool.path || null,
    };
  });
});

// 2.定义滚动分页处理器
const handleScroll = (event: UIEvent) => {
  // 2.1 获取滚动距离、可滚动的最大距离、客户端/浏览器窗口的高度
  const { scrollTop, scrollHeight, clientHeight } = event.target as HTMLElement

  // 2.2 判断是否滑动到底部
  if (scrollTop + clientHeight >= scrollHeight - 10) {
    if (getMcpToolProvidersLoading.value) return
    loadMcpToolProviders(false, String(route.query?.search_word ?? ''))
  }
}

// 3.定义打开更新模态窗
const handleUpdate = async () => {
  // 3.1 获取当前显示的provider_id
  const provider_id = mcp_tool_providers.value[showIdx.value]['id']

  // 3.2 根据拿到的id获取该工具提供商的详情信息
  await loadMcpToolProvider(provider_id)

  // 3.3 更新form表单数据
  formRef.value?.resetFields()
  form.value.fileList = [{ uid: '1', name: '插件图标', url: mcp_tool_provider.value.icon }]
  form.value.icon = mcp_tool_provider.value.icon
  form.value.name = mcp_tool_provider.value.name
  form.value.description = mcp_tool_provider.value.description
  form.value.mcp_schema = mcp_tool_provider.value.mcp_schema
  form.value.headers = mcp_tool_provider.value.headers

  showUpdateModal.value = true
}

// 4.定义删除工具提供者处理器
const handleDelete = () => {
  // 4.1 提取选中数据条目的提供者id
  const provider_id = mcp_tool_providers.value[showIdx.value]['id']

  // 4.2 调用删除Api工具提供者处理器
  handleDeleteMcpToolProvider(provider_id, () => {
    // 4.3 关闭模态窗+抽屉
    handleCancel()
    showIdx.value = -1

    // 4.4 重新加载数据
    loadMcpToolProviders(true, String(route.query?.search_word ?? ''))
  })
}

// 提交模态窗处理器
const handleSubmit = async ({
                              values,
                              errors,
                            }: {
  values: Record<string, any>
  errors: Record<string, ValidatedError> | undefined
}) => {
  // 1.如果存在错误则直接结束
  if (errors) return

  // 2.根据不同的类型发起不同的请求
  if (props.createType === 'mcp_tool_provider') {
    // 3.调用处理器发起创建请求
    await handleCreateMcpToolProvider(values as CreateMcpToolProviderRequest)
  } else if (showUpdateModal.value) {
    // 4.调用接口发起更新API工具请求
    await handleUpdateMcpToolProvider(
      mcp_tool_providers.value[showIdx.value]['id'],
      values as CreateMcpToolProviderRequest,
    )
  }

  // 5.执行后续操作，涵盖隐藏模态窗、隐藏抽屉
  handleCancel()
  showIdx.value = -1

  // 6.重新加载数据
  await loadMcpToolProviders(true, String(route.query?.search_word ?? ''))
}

// 取消显示模态窗处理器
const handleCancel = () => {
  // 1.重置整个表单的数据
  formRef.value?.resetFields()

  // 2.隐藏表单模态窗
  emits('update:create-type', '')
  showUpdateModal.value = false
}

// 页面DOM加载完毕初始化数据
onMounted(() => loadMcpToolProviders(true, String(route.query?.search_word ?? '')))

// 监听路由query变化
watch(
  () => route.query?.search_word,
  (newValue) => {
    loadMcpToolProviders(true, String(newValue))
  },
)

// 监听路由create_type变化
watch(
  () => route.query?.create_type,
  (newValue) => {
    if (newValue === 'mcp_tool_provider') emits('update:create-type', 'mcp_tool_provider')
  },
  { immediate: true },
)
</script>

<template>
  <a-spin
    :loading="loading"
    class="block h-full w-full scrollbar-w-none overflow-scroll"
    @scroll="handleScroll"
  >
    <!-- 底部插件列表 -->
    <a-row :gutter="[20, 20]" class="flex-1">
      <!-- 有数据的UI状态 -->
      <a-col v-for="(provider, idx) in mcp_tool_providers" :key="provider.name" :span="6">
        <a-card hoverable class="cursor-pointer rounded-lg" @click="showIdx = Number(idx)">
          <!-- 顶部提供商名称 -->
          <div class="flex items-center gap-3 mb-3">
            <!-- 左侧图标 -->
            <a-avatar :size="40" shape="square" :image-url="provider.icon" />
            <!-- 右侧工具信息 -->
            <div class="flex flex-col">
              <div class="text-base text-gray-900 font-bold">{{ provider.name }}</div>
              <div class="text-xs text-gray-500 line-clamp-1">
                提供商 {{ provider.name }} · {{ provider.tools.length }} 插件
              </div>
            </div>
          </div>
          <!-- 提供商的描述信息 -->
          <div class="leading-[18px] text-gray-500 h-[72px] line-clamp-4 mb-2">
            {{ provider.description }}
          </div>
          <!-- 提供商的发布信息 -->
          <div class="flex items-center gap-1.5">
            <a-avatar :size="18" class="bg-blue-700">
              <icon-user />
            </a-avatar>
            <div class="text-xs text-gray-400">
              慕小课 · 编辑时间
              {{ moment(provider.created_at * 1000).format('MM-DD HH:mm') }}
            </div>
          </div>
        </a-card>
      </a-col>
      <!-- 没数据的UI状态 -->
      <a-col v-if="mcp_tool_providers.length === 0" :span="24">
        <a-empty
          description="没有可用的API插件"
          class="h-[400px] flex flex-col items-center justify-center"
        />
      </a-col>
    </a-row>
    <!-- 加载器 -->
    <a-row v-if="paginator.total_page >= 2">
      <!-- 加载数据中 -->
      <a-col v-if="paginator.current_page <= paginator.total_page" :span="24" align="center">
        <a-space class="my-4">
          <a-spin />
          <div class="text-gray-400">加载中</div>
        </a-space>
      </a-col>
      <!-- 数据加载完成 -->
      <a-col v-else :span="24" align="center">
        <div class="text-gray-400 my-4">数据已加载完成</div>
      </a-col>
    </a-row>
    <!-- 卡片抽屉 -->
    <a-drawer
      :visible="showIdx != -1"
      :width="350"
      :footer="false"
      title="工具详情"
      :drawer-style="{ background: '#F9FAFB' }"
      @cancel="showIdx = -1"
    >
      <!-- 外部容器，用于判断showIdx是否为-1，为-1的时候就不显示 -->
      <div v-if="showIdx != -1" class="">
        <!-- 顶部提供商名称 -->
        <div class="flex items-center gap-3 mb-3">
          <!-- 左侧图标 -->
          <a-avatar :size="40" shape="square" :image-url="mcp_tool_providers[showIdx].icon" />
          <!-- 右侧工具信息 -->
          <div class="flex flex-col">
            <div class="text-base text-gray-900 font-bold">
              {{ mcp_tool_providers[showIdx].name }}
            </div>
            <div class="text-xs text-gray-500 line-clamp-1">
              提供商 {{ mcp_tool_providers[showIdx].name }} ·
              {{ mcp_tool_providers[showIdx].tools.length }} 插件
            </div>
          </div>
        </div>
        <!-- 提供商的描述信息 -->
        <div class="leading-[18px] text-gray-500 mb-4">
          {{ mcp_tool_providers[showIdx].description }}
        </div>
        <!-- 编辑按钮 -->
        <a-button
          :loading="getMcpToolProviderLoading"
          type="dashed"
          long
          class="mb-2 rounded-lg"
          @click="handleUpdate"
        >
          <template #icon>
            <icon-settings />
          </template>
          编辑工具
        </a-button>
        <!-- 分隔符 -->
        <hr class="my-4" />
        <!-- 提供者工具 -->
        <div class="flex flex-col gap-2">
          <div class="text-xs text-gray-500">
            包含 {{ mcp_tool_providers[showIdx].tools.length }} 个工具
          </div>
          <!-- 工具列表 -->
          <a-card
            v-for="tool in mcp_tool_providers[showIdx].tools"
            :key="tool.name"
            class="cursor-pointer flex flex-col rounded-xl"
          >
            <!-- 工具名称 -->
            <div class="font-bold text-gray-900 mb-2">{{ tool.name }}</div>
            <!-- 工具描述 -->
            <div class="text-gray-500 text-xs">{{ tool.description }}</div>
            <!-- 工具参数 -->
            <div v-if="tool.inputs.length > 0" class="">
              <!-- 分隔符 -->
              <div class="flex items-center gap-2 my-4">
                <div class="text-xs font-bold text-gray-500">参数</div>
                <hr class="flex-1" />
              </div>
              <!-- 参数列表 -->
              <div class="flex flex-col gap-4">
                <div v-for="input in tool.inputs" :key="input.name" class="flex flex-col gap-2">
                  <!-- 上半部分 -->
                  <div class="flex items-center gap-2 text-xs">
                    <div class="text-gray-900 font-bold">{{ input.name }}</div>
                    <div class="text-gray-500">{{ typeMap[input.type] }}</div>
                    <div v-if="input.required" class="text-red-700">必填</div>
                  </div>
                  <!-- 参数描述信息 -->
                  <div class="text-xs text-gray-500">{{ input.description }}</div>
                </div>
              </div>
            </div>
          </a-card>
        </div>
      </div>
    </a-drawer>
    <!-- 新建/修改模态窗 -->
    <a-modal
      :width="630"
      :visible="props.createType === 'mcp_tool_provider' || showUpdateModal"
      hide-title
      :footer="false"
      modal-class="rounded-xl"
      @cancel="handleCancel"
    >
      <!-- 顶部标题 -->
      <div class="flex items-center justify-between">
        <div class="text-lg font-bold text-gray-700">
          {{ props.createType === 'tool' ? '新建' : '更新' }}插件
        </div>
        <a-button type="text" class="!text-gray-700" size="small" @click="handleCancel">
          <template #icon>
            <icon-close />
          </template>
        </a-button>
      </div>
      <!-- 中间表单 -->
      <div class="pt-6">
        <a-form ref="formRef" :model="form" @submit="handleSubmit" layout="vertical">
          <a-form-item
            field="fileList"
            hide-label
            :rules="[{ required: true, message: '插件图标不能为空' }]"
          >
            <a-upload
              :limit="1"
              list-type="picture-card"
              accept="image/png, image/jpeg"
              class="!w-auto mx-auto"
              v-model:file-list="form.fileList"
              image-preview
              :custom-request="
                (option) => {
                  const uploadTask = async () => {
                    const { fileItem, onSuccess, onError } = option
                    await handleUploadImage(fileItem.file as File)
                    form.icon = image_url
                    onSuccess(image_url)
                  }

                  uploadTask()

                  return {}
                }
              "
              :on-before-remove="
                async (fileItem) => {
                  form.icon = ''
                  return true
                }
              "
            />
          </a-form-item>
          <a-form-item
            field="name"
            label="插件名称"
            asterisk-position="end"
            :rules="[{ required: true, message: '插件名称不能为空' }]"
          >
            <a-input
              v-model="form.name"
              placeholder="请输入插件名称，确保名称含义清晰"
              show-word-limit
              :max-length="60"
            />
          </a-form-item>
          <a-form-item
              field="description"
              label="插件描述"
              asterisk-position="end"
              :rules="[{ required: true, message: '插件描述不能为空' }]"
          >
            <a-textarea
                v-model="form.description"
                :auto-size="{ minRows: 2, maxRows: 4 }"
                placeholder="请输入插件描述，确保描述含义清晰"
                show-word-limit
                :max-length="200"
            />
          </a-form-item>


          <a-form-item
            field="mcp_schema"
            label="MCP Schema"
            asterisk-position="end"
            :rules="[{ required: true, message: 'MCP Schema不能为空' }]"
          >
            <a-textarea
              v-model="form.mcp_schema"
              :auto-size="{ minRows: 4, maxRows: 6 }"
              placeholder="在此处输入您的MCP Schema"
              @blur="
                () => {
                  if (form.mcp_schema.trim() !== '') {
                    // 调用验证openapi_schema接口
                    handleValidateMcpSchema(form.mcp_schema)
                  }
                }
              "
            />
          </a-form-item>
          <a-form-item label="可用工具">
            <!-- 可用工具表格 -->
            <div class="rounded-lg border border-gray-200 w-full overflow-x-auto">
              <table class="w-full leading-[18px] text-xs text-gray-700 font-normal">
                <thead class="text-gray-500">
                <tr class="border-b border-gray-200">
                  <th class="p-2 pl-3 font-medium">名称</th>
                  <th class="p-2 pl-3 font-medium w-[236px]">描述</th>
                  <th class="p-2 pl-3 font-medium">方法</th>
                  <th class="p-2 pl-3 font-medium">路径</th>
                </tr>
                </thead>
                <tbody>
                <tr
                  v-for="(tool, idx) in tools"
                  :key="idx"
                  class="border-b last:border-0 border-gray-200 text-gray-700"
                >
                  <td class="p-2 pl-3">{{ tool.name }}</td>
                  <td class="p-2 pl-3 w-[236px]">{{ tool.description }}</td>
                  <td class="p-2 pl-3">{{ tool.method }}</td>
                  <td class="p-2 pl-3 w-[62px]">{{ tool.path }}</td>
                </tr>
                </tbody>
              </table>
            </div>
          </a-form-item>
          <a-form-item label="Headers">
            <!-- 请求头表单 -->
            <div class="rounded-lg border border-gray-200 w-full overflow-x-auto">
              <table class="w-full leading-[18px] text-xs text-gray-700 font-normal mb-3">
                <thead class="text-gray-500">
                <tr class="border-b border-gray-200">
                  <th class="p-2 pl-3 font-medium">Key</th>
                  <th class="p-2 pl-3 font-medium">Value</th>
                  <th class="p-2 pl-3 font-medium w-[50px]">操作</th>
                </tr>
                </thead>
                <tbody v-if="form.headers.length > 0" class="border-b border-gray-200">
                <tr
                  v-for="(header, idx) in form.headers"
                  :key="idx"
                  class="border-b last:border-0 border-gray-200"
                >
                  <td class="p-2 pl-3">
                    <a-form-item :field="`headers[${idx}].key`" hide-label class="m-0">
                      <a-input v-model="header.key" placeholder="请输入请求头键名" />
                    </a-form-item>
                  </td>
                  <td class="p-2 pl-3">
                    <a-form-item :field="`headers[${idx}].value`" hide-label class="m-0">
                      <a-input v-model="header.value" placeholder="请输入请求头键值内容" />
                    </a-form-item>
                  </td>
                  <td class="p-2 pl-3">
                    <a-button
                      size="mini"
                      type="text"
                      class="!text-gray-700"
                      @click="form.headers.splice(idx, 1)"
                    >
                      <template #icon>
                        <icon-delete />
                      </template>
                    </a-button>
                  </td>
                </tr>
                </tbody>
              </table>
              <a-button
                size="mini"
                class="rounded ml-3 mb-3 !text-gray-700"
                @click="form.headers.push({ key: '', value: '' })"
              >
                <template #icon>
                  <icon-plus />
                </template>
                增加参数
              </a-button>
            </div>
          </a-form-item>
          <!-- 底部按钮 -->
          <div class="flex items-center justify-between">
            <div class="">
              <a-button
                v-if="showUpdateModal"
                class="rounded-lg !text-red-700"
                @click="handleDelete"
              >
                删除
              </a-button>
            </div>
            <a-space :size="16">
              <a-button class="rounded-lg" @click="handleCancel">取消</a-button>
              <a-button
                :loading="updateMcpToolProviderLoading || createMcpToolProviderLoading"
                type="primary"
                html-type="submit"
                class="rounded-lg"
              >
                保存
              </a-button>
            </a-space>
          </div>
        </a-form>
      </div>
    </a-modal>
  </a-spin>
</template>

<style scoped></style>
