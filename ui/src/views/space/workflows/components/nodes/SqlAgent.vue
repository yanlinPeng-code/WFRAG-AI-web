<script setup lang="ts">
import { Handle, type NodeProps, Position, useVueFlow } from '@vue-flow/core'
import { computed } from 'vue'
// 1.定义自定义组件所需数据
const props = defineProps<NodeProps>()
const { edges, removeNodes } = useVueFlow()


// 2.计算当前节点是否有连线（孤立节点）
// const isIsolatedNode = computed(() => {
//   return !edges.value.some(edge =>
//     edge.source === props.id || edge.target === props.id
//   )
// })

// 3.定义删除节点处理函数
const handleDeleteNode = () => {

    removeNodes([props.id])

}


</script>

<template>
  <div
    class="flex flex-col gap-3 rounded-2xl p-3 bg-white border-[2px] border-transparent shadow-sm hover:shadow-md selected-border transition-all w-[360px]"
    style="position: relative;"
  >
    <div
      class="absolute   -top-2 -right-0 z-20 flex justify-end"
    >
      <el-dropdown>
      <span class="el-dropdown-link custom-dropdown-text " >
        ...<i class="el-icon-arrow-down el-icon--right"></i>
      </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleDeleteNode">删除</el-dropdown-item>

          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>



 <!-- 顶部节点标题 -->
    <div class="flex items-center gap-2">
      <a-avatar shape="square" :size="24" class="bg-sky-500 rounded-lg flex-shrink-0">
        <icon-robot :size="16" />
      </a-avatar>
      <div class="text-gray-700 font-semibold">{{ props.data?.title }}</div>
    </div>
    <!-- 输入变量列表 -->
    <div class="flex flex-col items-start bg-gray-100 rounded-lg p-3">
      <!-- 标题(分成左右两部分) -->
      <div class="w-full flex items-center gap-2 mb-2 text-gray-700 text-xs">
        <!-- 左侧变量名 -->
        <div class="w-[180px] flex-shrink-0 flex items-center gap-2 text-gray-700">
          <icon-caret-down />
          <div class="font-semibold">输入数据</div>
        </div>
        <!-- 右侧值信息 -->
        <div class="flex-1">值</div>
      </div>
      <!-- 输入变量列表 -->
      <div class="w-full flex flex-col gap-2">
        <div
          v-for="input in props.data?.inputs"
          :key="input.name"
          class="w-full flex items-center text-xs gap-2"
        >
          <!-- 左侧变量信息 -->
          <div class="w-[180px] flex-shrink-0 flex items-center gap-2">
            <div class="flex items-center gap-1">
              <div class="text-gray-700 line-clamp-1 break-all">{{ input.name }}</div>
              <div v-if="input.required" class="text-red-700 flex-shrink-0">*</div>
            </div>
            <div class="text-gray-500 bg-gray-200 px-1 py-0.5 rounded flex-shrink-0">
              {{ input.type }}
            </div>
          </div>
          <!-- 右侧变量引用 -->
          <div class="flex-1 flex">
            <div
              v-if="input.value.type == 'ref'"
              class="bg-white line-clamp-1 break-all text-gray-500 border px-1 py-0.5 rounded"
            >
              引用 / {{ input.value.content.ref_var_name }}
            </div>
            <div v-else class="text-gray-500 flex-1 px-1 py-0.5 line-clamp-1 break-all">
              {{ input.name === 'password' ? '****' : input.value.content }}
            </div>
          </div>
        </div>
        <div v-if="!props.data?.inputs?.length" class="text-gray-500 text-xs px-0.5">-</div>
      </div>
    </div>
    <!-- 提示词 -->
    <div class="flex flex-col items-start bg-gray-100 rounded-lg p-3">
      <!-- 标题 -->
      <div class="flex items-center gap-2 mb-2 text-gray-700">
        <icon-caret-down />
        <div class="text-xs font-semibold">提示词</div>
      </div>
      <!-- 内容 -->
      <div class="text-xs text-gray-700 leading-5 line-clamp-3">
        {{ props.data?.prompt ?? '-' }}
      </div>
    </div>
    <!-- 输出变量列表 -->
    <div class="flex flex-col items-start bg-gray-100 rounded-lg p-3">
      <!-- 标题 -->
      <div class="flex items-center gap-2 mb-2 text-gray-700">
        <icon-caret-down />
        <div class="text-xs font-semibold">输出数据</div>
      </div>
      <!-- 变量列表 -->
      <div class="flex flex-col gap-2">
        <div
          v-for="output in props.data?.outputs"
          :key="output.name"
          class="flex items-center gap-2 text-xs"
        >
          <div class="max-w-[180px] text-gray-700 line-clamp-1 break-all">{{ output.name }}</div>
          <div class="text-gray-500 bg-gray-200 px-1 py-0.5 rounded">{{ output.type }}</div>
        </div>
      </div>
    </div>
    <!-- 边起点句柄位置在右侧 -->
    <handle
      type="source"
      :position="Position.Right"
      class="!w-4 !h-4 !bg-blue-700 !text-white flex items-center justify-center"
    >
      <icon-plus :size="12" class="pointer-events-none" />
    </handle>
    <handle
      type="target"
      :position="Position.Left"
      class="!w-4 !h-4 !bg-blue-700 !text-white flex items-center justify-center"
    >
      <icon-plus :size="12" class="pointer-events-none" />
    </handle>
  </div>
</template>

<style scoped>

.selected-border {
  @apply border-blue-700;
}

/* 针对 Element UI Dropdown Link 的样式覆盖 */
.custom-dropdown-text {
  font-size: 35px !important; /* 强制字体大小为 20px，可以根据需要调整 */
  color: #333 !important; /* 确保字体颜色为深灰色，以便在白色背景上可见 */
}

/* 确保 Element UI 的箭头图标也可见 */
.el-dropdown-link .el-icon-arrow-down {
  color: #333 !important; /* 强制箭头图标颜色为深灰色 */
  font-size: 16px !important; /* 调整箭头图标大小 */
}

</style>
<!--    &lt;!&ndash; 节点标题信息 &ndash;&gt;-->
<!--    <div class="flex items-center gap-2">-->
<!--      <a-avatar shape="square" :size="24" class="bg-yellow-500 rounded-lg flex-shrink-0">-->
<!--        <icon-robot :size="16" />-->
<!--      </a-avatar>-->
<!--      <div class="text-gray-700 font-semibold">{{ props.data?.title || 'SQL Agent' }}</div>-->
<!--    </div>-->
<!--    &lt;!&ndash; 数据库连接信息 &ndash;&gt;-->
<!--    <div class="flex flex-col items-start bg-gray-100 rounded-lg p-3">-->
<!--      <div class="flex items-center gap-2 mb-2 text-gray-700">-->
<!--        <icon-caret-down />-->
<!--        <div class="text-xs font-semibold">数据库连接</div>-->
<!--      </div>-->
<!--      <div class="text-xs text-gray-700">-->
<!--        <div>Host: {{ dbInfo.host }}</div>-->
<!--        <div>Port: {{ dbInfo.port }}</div>-->
<!--        <div>User: {{ dbInfo.user }}</div>-->
<!--        <div>Database: {{ dbInfo.database }}</div>-->
<!--      </div>-->
<!--    </div>-->
<!--    &lt;!&ndash; 用户Query展示 &ndash;&gt;-->
<!--    <div class="flex flex-col items-start bg-gray-100 rounded-lg p-3">-->
<!--      <div class="flex items-center gap-2 mb-2 text-gray-700">-->
<!--        <icon-caret-down />-->
<!--        <div class="text-xs font-semibold">用户Query</div>-->
<!--      </div>-->
<!--      <div class="text-xs text-gray-700 break-all">-->
<!--        {{ props.data?.meta?.query || '-' }}-->
<!--      </div>-->
<!--    </div>-->
<!--    &lt;!&ndash; Agent思考链展示 &ndash;&gt;-->
<!--    <div class="flex flex-col items-start bg-gray-100 rounded-lg p-3">-->
<!--      <div class="flex items-center gap-2 mb-2 text-gray-700">-->
<!--        <icon-caret-down />-->
<!--        <div class="text-xs font-semibold">Agent思考链</div>-->
<!--      </div>-->
<!--      <div class="flex flex-col gap-1 w-full">-->
<!--        <div-->
<!--          v-for="thought in props.data?.meta?.agent_thoughts || []"-->
<!--          :key="thought.id"-->
<!--          class="text-xs text-gray-700 bg-white rounded px-2 py-1 border border-gray-200"-->
<!--        >-->
<!--          <div class="font-semibold text-gray-500">[{{ thought.event }}]</div>-->
<!--          <div>思考: {{ thought.thought }}</div>-->
<!--          <div v-if="thought.observation">观察: {{ thought.observation }}</div>-->
<!--          <div v-if="thought.tool">工具: {{ thought.tool }}</div>-->
<!--          <div v-if="thought.tool_input">输入: {{ JSON.stringify(thought.tool_input) }}</div>-->
<!--        </div>-->
<!--        <div v-if="!props.data?.meta?.agent_thoughts?.length" class="text-gray-500 text-xs px-0.5">-</div>-->
<!--      </div>-->
<!--    </div>-->
<!--    &lt;!&ndash; 执行结果 &ndash;&gt;-->
<!--    <div class="flex flex-col items-start bg-gray-100 rounded-lg p-3">-->
<!--      <div class="flex items-center gap-2 mb-2 text-gray-700">-->
<!--        <icon-caret-down />-->
<!--        <div class="text-xs font-semibold">执行结果</div>-->
<!--      </div>-->
<!--      <div class="text-xs text-gray-700 break-all">-->
<!--        {{ props.data?.outputs?.[0]?.value?.content || '-' }}-->
<!--      </div>-->
<!--    </div>-->
<!--    &lt;!&ndash; 连接句柄 &ndash;&gt;-->
<!--    <handle-->
<!--      type="source"-->
<!--      :position="Position.Right"-->
<!--      class="!w-4 !h-4 !bg-blue-700 !text-white flex items-center justify-center"-->
<!--    >-->
<!--      <icon-plus :size="12" class="pointer-events-none" />-->
<!--    </handle>-->
<!--    <handle-->
<!--      type="target"-->
<!--      :position="Position.Left"-->
<!--      class="!w-4 !h-4 !bg-blue-700 !text-white flex items-center justify-center"-->
<!--    >-->
<!--      <icon-plus :size="12" class="pointer-events-none" />-->
<!--    </handle>-->
<!--  </div>-->
<!--</template>-->

<!--<style scoped>-->
<!--.selected-border {-->
<!--  @apply border-blue-700;-->
<!--}-->
<!--</style>-->