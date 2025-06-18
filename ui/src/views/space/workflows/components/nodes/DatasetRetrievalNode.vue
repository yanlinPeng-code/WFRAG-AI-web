<script setup lang="ts">
import { Handle, type NodeProps, Position ,useVueFlow} from '@vue-flow/core'
import {computed} from 'vue'
// 1.定义自定义组件所需数据
const props = defineProps<NodeProps>()
const { edges, removeNodes } = useVueFlow()



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

    <!-- 节点标题信息 -->
    <div class="flex items-center gap-2">
      <a-avatar shape="square" :size="24" class="bg-violet-500 rounded-lg flex-shrink-0">
        <icon-storage :size="16" />
      </a-avatar>
      <div class="text-gray-700 font-semibold">{{ props.data?.title }}</div>
    </div>
    <!-- 输入变量列表 -->
    <div class="flex flex-col items-start bg-gray-100 rounded-lg p-3">
      <!-- 标题(分成左右两部分) -->
      <div class="w-full flex items-center mb-2 text-gray-700 text-xs gap-2">
        <!-- 左侧变量名 -->
        <div class="w-[180px] flex-shrink-0 flex items-center gap-2 text-gray-700">
          <icon-caret-down />
          <div class="font-semibold">输入数据</div>
        </div>
        <!-- 右侧变量值 -->
        <div class="flex-1 font-semibold">值</div>
      </div>
      <!-- 输入变量 -->
      <div class="w-full flex flex-col gap-2">
        <div
          v-for="input in props.data.inputs"
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
              {{ input.value.content }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 关联知识库 -->
    <div class="flex flex-col items-start bg-gray-100 rounded-lg p-3">
      <!-- 标题 -->
      <div class="flex items-center gap-2 mb-2 text-gray-700">
        <icon-caret-down />
        <div class="text-xs font-semibold">关联知识库</div>
      </div>
      <!-- 关联知识库列表 -->
      <div class="flex flex-col gap-2">
        <div
          v-for="dataset in props.data?.meta?.datasets ?? []"
          :key="dataset.id"
          class="flex items-center gap-2 text-xs"
        >
          <!-- 左侧知识库图标 -->
          <a-avatar :size="16" shape="square" :image-url="dataset?.icon" />
          <!-- 右侧知识库名称 -->
          <div class="text-gray-700">{{ dataset?.name }}</div>
        </div>
        <div v-if="!props.data?.meta?.datasets?.length" class="text-gray-500 text-xs px-0.5">-</div>
      </div>
    </div>
    <!-- 输出变量 -->
    <div class="flex flex-col items-start bg-gray-100 rounded-lg p-3">
      <!-- 标题 -->
      <div class="flex items-center gap-2 mb-2 text-gray-700">
        <icon-caret-down />
        <div class="text-xs font-semibold">输出数据</div>
      </div>
      <!-- 变量容器 -->
      <div class="flex flex-col gap-2">
        <div
          v-for="output in props.data?.outputs"
          :key="output.name"
          class="flex items-center gap-2 text-xs"
        >
          <div class="flex items-center gap-1">
            <div class="text-gray-700">{{ output.name }}</div>
          </div>
          <div class="text-gray-500 bg-gray-200 px-1 py-0.5 rounded">{{ output.type }}</div>
        </div>
      </div>
    </div>
    <!-- 大模型节点-连接句柄 -->
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
.selected {
  .selected-border {
    @apply border-blue-700;
  }
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
