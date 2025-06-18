<script setup lang="ts">
import { nextTick, type PropType, ref, watch } from 'vue'
import { useUpdateDraftAppConfig } from '@/hooks/use-app'
import { cloneDeep, isEqual } from 'lodash'
import { Message } from '@arco-design/web-vue'
import {useGetMcpToolProvidersWithPage} from '@/hooks/use-mcp'
// 1.定义自定义组件所需数据
const props = defineProps({
  app_id: { type: String, default: '', required: true },
  mcp_providers: {
    type: Array as PropType<
      {
        id: string
        name: string
        icon: string
        description: string
      }[]
    >,
    default: () => [],
    required: true,
  },
})
const emits = defineEmits(['update:mcp_tools'])
const { loading: updateDraftAppConfigLoading, handleUpdateDraftAppConfig } =
  useUpdateDraftAppConfig()
const { loading, paginator, mcp_tool_providers: mcp_tool_providers, loadMcpToolProviders } = useGetMcpToolProvidersWithPage()
const mcpProvidersModalVisible = ref(false)
const isMcpProvidersInit = ref(false)
const activateMcpProviders = ref<Record<string, any>[]>([])
const originMcpProviders = ref<Record<string, any>[]>([])

// 2.定义滚动数据分页处理器
const handleScroll = async (event: UIEvent) => {
  // 2.1 获取滚动距离、可滚动的最大距离、客户端/浏览器窗口的高度
  const { scrollTop, scrollHeight, clientHeight } = event.target as HTMLElement

  // 2.2 判断是否滑动到底部
  if (scrollTop + clientHeight >= scrollHeight - 10) {
    if (loading.value) return
    await loadMcpToolProviders(false, '')
  }
}
console.log(props.mcp_providers)

// 3.定义判断工作流数据是否发生变化函数
const isMcpProvidersModified = () => {
  return isEqual(activateMcpProviders.value, originMcpProviders.value)
}

// 4.定义取消模态窗处理器
const handleCancelMcpProvidersModal = () => {
  // 4.1 隐藏模态窗
  mcpProvidersModalVisible.value = false

  // 4.2 还原初始值
  activateMcpProviders.value = originMcpProviders.value
  isMcpProvidersInit.value = false
}

// 7.工作流选择处理器
const handleSelectMcpProvider = (idx: any) => {
  // 7.1 提取对应的工作流id
  const mcp_provider = mcp_tool_providers.value[idx]

  // 7.2 检测id是否选中，如果是选中则删除
  if (activateMcpProviders.value.some((activateMcpProvider) => activateMcpProvider.id === mcp_provider.id)) {
    activateMcpProviders.value = activateMcpProviders.value.filter(
      (activateMcpProvider) => activateMcpProvider.id !== mcp_provider.id,
    )
  } else {
    // 7.3 检测已关联的工作流数量
    if (activateMcpProviders.value.length >= 5) {
      Message.warning('关联工作流已超过5个，无法继续关联')
      return
    }
    // 7.4 添加数据到激活工作流列表
    activateMcpProviders.value.push({
      id: mcp_provider.id,
      name: mcp_provider.name,
      icon: mcp_provider.icon,
      description: mcp_provider.description,
    })
  }
}

// 8.提交更新关联工作流
const handleSubmitMcpProviders = async () => {
  // 8.1 处理数据并完成API接口提交
  await handleUpdateDraftAppConfig(props.app_id, {
    mcp_tools: activateMcpProviders.value.map((activateMcpProvider) => activateMcpProvider.id),
  })

  // 8.2 接口更新更新成功，同步表单信息
  originMcpProviders.value = activateMcpProviders.value
  await nextTick()

  // 8.3 双向同步更新props中的数据
  emits('update:mcp_tools', activateMcpProviders.value)

  // 8.4 隐藏模态窗
  handleCancelMcpProvidersModal()
}

// 10.监听草稿配置关联的工作流列表
watch(
  () => props.mcp_providers,
  (newValue) => {
    // 10.1 检测数据是否初始化
    if (!isMcpProvidersInit.value || !isMcpProvidersModified()) {
      // 10.2 判断草稿配置是否已传递配置
      if (newValue && newValue.length > 0) {
        // 10.3 赋初始值
        const initData = props.mcp_providers.map((mcp_provider) => {
          return {
            id: mcp_provider.id,
            name: mcp_provider.name,
            icon: mcp_provider.icon,
            description: mcp_provider.description,
          }
        })
        activateMcpProviders.value = cloneDeep(initData)
        originMcpProviders.value = cloneDeep(initData)

        // 10.4 修改初始化状态
        isMcpProvidersInit.value = true
      }
    }
  },
  { immediate: true, deep: true },
)

// 12.监听知识库模态窗显示or隐藏
watch(
  () => mcpProvidersModalVisible.value,
  async (newValue) => {
    // 12.1 显示状态，重新加载数据，获取最新的知识库列表
    if (newValue) {
      await loadMcpToolProviders(true, '')
    } else {
      // 12.2 隐藏状态，清空数据
      mcp_tool_providers.value.splice(0, mcp_tool_providers.value.length)
    }
  },
)
</script>

<template>
  <div class="">
    <a-collapse-item key="mcp_providers" class="app-ability-item">
      <template #header>
        <div class="text-gray-700 font-bold">mcp提供商插件</div>
      </template>
      <template #extra>
        <a-button
          size="mini"
          type="text"
          class="!text-gray-700"
          @click.stop="mcpProvidersModalVisible = true"
        >
          <template #icon>
            <icon-plus />
          </template>
        </a-button>
      </template>
      <div v-if="props.mcp_providers?.length > 0" class="flex flex-col gap-1">
        <div
          v-for="(mcp_provider, idx) in props.mcp_providers"
          :key="mcp_provider.id"
          class="flex items-center justify-between bg-white p-3 rounded-lg cursor-pointer hover:shadow-sm group"
        >
          <!-- 左侧工作流信息 -->
          <div class="flex items-center gap-2">
            <!-- 图标 -->
            <a-avatar
              :size="36"
              shape="square"
              class="rounded flex-shrink-0"
              :image-url="mcp_provider.icon"
            />
            <!-- 名称与描述信息 -->
            <div class="flex flex-col flex-1 gap-1 h-9">
              <div class="text-gray-700 font-bold leading-[18px] line-clamp-1 break-all">
                {{ mcp_provider.name }}
              </div>
              <div class="text-gray-500 text-xs line-clamp-1 break-all">
                {{ mcp_provider.description }}
              </div>
            </div>
          </div>
          <!-- 右侧删除按钮 -->
          <a-button
            size="mini"
            type="text"
            class="hidden group-hover:block flex-shrink-0 ml-2 !text-red-700 rounded"
            @click="
              async () => {
                // 1.清除props中指定的数据
                const newMcpProviders = [...props.mcp_providers]
                newMcpProviders.splice(idx, 1)

                // 2.提交草稿配置到接口
                await handleUpdateDraftAppConfig(props.app_id, {
                  mcp_tools: newMcpProviders.map((item) => item.id),
                })

                // 3.更新数据并确保数据完成更新
                isMcpProvidersInit = false
                emits('update:mcp_tools', newMcpProviders)
              }
            "
          >
            <template #icon>
              <icon-delete />
            </template>
          </a-button>
        </div>
      </div>
      <div v-else class="text-xs text-gray-500 leading-[22px]">
        MCP提供商提供多种工具,供模型使用
      </div>
    </a-collapse-item>
    <!-- 工作流模态窗 -->
    <a-modal
      :visible="mcpProvidersModalVisible"
      hide-title
      :footer="false"
      :width="400"
      class="mcp-providers-modal"
      modal-class="h-[calc(100vh-32px)] right-4"
      @cancel="handleCancelMcpProvidersModal"
    >
      <!-- 顶部标题 -->
      <div class="flex items-center justify-between mb-6">
        <div class="text-lg font-bold text-gray-700">选择关联mcp提供商</div>
        <a-button
          type="text"
          class="!text-gray-700"
          size="small"
          @click="handleCancelMcpProvidersModal"
        >
          <template #icon>
            <icon-close />
          </template>
        </a-button>
      </div>
      <!-- 中间工作流容器 -->
      <div class="h-[calc(100vh-180px)] mb-4 overflow-scroll scrollbar-w-none">
        <a-spin
          :loading="loading"
          class="block h-full w-full scrollbar-w-none overflow-scroll"
          @scroll="handleScroll"
        >
          <!-- 工作流列表 -->
          <div class="flex flex-col gap-2">
            <!-- 有数据UI状态 -->
            <div
              v-for="(mcp_provider, idx) in mcp_tool_providers"
              :key="mcp_provider.id"
              :class="`flex items-center gap-2 border px-3 py-2 rounded-lg cursor-pointer hover:bg-blue-50 hover:border-blue-700 ${activateMcpProviders.some((activateMcpProvider) => activateMcpProvider.id === mcp_provider.id) ? 'bg-blue-50 border-blue-700' : ''}`"
              @click="() => handleSelectMcpProvider(idx)"
            >
              <a-avatar
                :size="24"
                shape="square"
                class="flex-shrink-0 rounded"
                :image-url="mcp_provider.icon"
              />
              <div class="line-clamp-1 text-gray-500 flex-1">{{ mcp_provider.name }}</div>
            </div>
            <!-- 无数据UI状态 -->
            <a-empty
              v-if="mcp_tool_providers.length === 0"
              description="没有可用的mcp提供商"
              class="h-[400px] flex flex-col items-center justify-center"
            />
          </div>
          <!-- 加载器 -->
          <a-row v-if="paginator.total_page >= 2">
            <!-- 加载数据中 -->
            <a-col
              v-if="paginator.current_page <= paginator.total_page"
              :span="24"
              class="!text-center"
            >
              <a-space class="my-4">
                <a-spin />
                <div class="text-gray-400">加载中</div>
              </a-space>
            </a-col>
            <!-- 数据加载完成 -->
            <a-col v-else :span="24" class="!text-center">
              <div class="text-gray-400 my-4">数据已加载完成</div>
            </a-col>
          </a-row>
        </a-spin>
      </div>
      <!-- 底部选中工作流及按钮 -->
      <div class="flex items-center justify-between">
        <!-- 左侧提示文字 -->
        <div class="">{{ activateMcpProviders.length }} 个mcp提供商被选中</div>
        <!-- 按钮组 -->
        <a-space :size="12">
          <a-button class="rounded-lg" @click="handleCancelMcpProvidersModal">取消</a-button>
          <a-button
            :loading="updateDraftAppConfigLoading"
            type="primary"
            class="rounded-lg"
            @click="handleSubmitMcpProviders"
          >
            添加
          </a-button>
        </a-space>
      </div>
    </a-modal>
  </div>
</template>

<style>
.mcp-providers-modal {
  .arco-modal-wrapper {
    text-align: right;
  }
}
</style>
