<!--<script setup lang="ts">-->
<!--import { type PropType, ref } from 'vue'-->
<!--import { QueueEvent } from '@/config'-->

<!--// 1.定义自定义组件所需数据-->
<!--const props = defineProps({-->
<!--  loading: { type: Boolean, default: false, required: true },-->
<!--  agent_thoughts: {-->
<!--    type: Array as PropType<Record<string, any>[]>,-->
<!--    default: () => [],-->
<!--    required: true,-->
<!--  },-->
<!--})-->

<!--const visible = ref(false)-->
<!--</script>-->

<!--<template>-->
<!--  &lt;!&ndash; 智能体推理步骤 &ndash;&gt;-->
<!--  <div :class="`flex flex-col rounded-2xl border ${visible ? 'w-[320px]' : 'w-[180px]'}`">-->
<!--    <div-->
<!--      :class="`flex items-center justify-between h-10 rounded-2xl bg-gray-100 px-4 text-gray-700 cursor-pointer w-auto ${visible ? 'rounded-bl-none rounded-br-none' : ''}`"-->
<!--      @click="visible = !visible"-->
<!--    >-->
<!--      &lt;!&ndash; 左侧图标与标题 &ndash;&gt;-->
<!--      <div class="flex items-center gap-2">-->
<!--        <icon-list />-->
<!--        {{ visible ? '隐藏' : '显示' }}运行流程-->
<!--      </div>-->
<!--      &lt;!&ndash; 右侧图标 &ndash;&gt;-->
<!--      <div class="">-->
<!--        <template v-if="props.loading">-->
<!--          <icon-loading />-->
<!--        </template>-->
<!--        <template v-else>-->
<!--          <icon-up v-if="visible" />-->
<!--          <icon-down v-else />-->
<!--        </template>-->
<!--      </div>-->
<!--    </div>-->
<!--    &lt;!&ndash; 底部内容 &ndash;&gt;-->
<!--    <a-collapse class="agent-thought" v-if="visible" destroy-on-hide :bordered="false">-->
<!--      <a-collapse-item-->
<!--        v-for="agent_thought in props.agent_thoughts.filter((item: any) =>-->
<!--        -->
<!--          [-->
<!--            QueueEvent.longTermMemoryRecall,-->
<!--            QueueEvent.agentThought,-->
<!--            QueueEvent.datasetRetrieval,-->
<!--            QueueEvent.agentAction,-->
<!--            QueueEvent.agentMessage,-->
<!--          ].includes(item.event),-->
<!--        )"-->
<!--        :key="agent_thought.id"-->
<!--      >-->
<!--        <template #expand-icon>-->

<!--          <icon-file v-if="agent_thought.event === QueueEvent.longTermMemoryRecall" />-->
<!--          <icon-language v-else-if="agent_thought.event === QueueEvent.agentThought" />-->
<!--          <icon-storage v-else-if="agent_thought.event === QueueEvent.datasetRetrieval" />-->
<!--          <icon-tool v-else-if="agent_thought.event === QueueEvent.agentAction" />-->
<!--          <icon-message v-else-if="agent_thought.event === QueueEvent.agentMessage" />-->
<!--        </template>-->
<!--        <template #header>-->
<!--          <div class="text-gray-700" v-if="agent_thought.event === QueueEvent.longTermMemoryRecall">-->
<!--            长期记忆召回-->
<!--          </div>-->
<!--          <div class="text-gray-700" v-if="agent_thought.event === QueueEvent.agentThought">-->
<!--            智能体推理-->
<!--          </div>-->
<!--          <div class="text-gray-700" v-if="agent_thought.event === QueueEvent.datasetRetrieval">-->
<!--            搜索知识库-->
<!--          </div>-->
<!--          <div class="text-gray-700" v-if="agent_thought.event === QueueEvent.agentAction">-->
<!--            调用工具-->
<!--          </div>-->
<!--          <div class="text-gray-700" v-if="agent_thought.event === QueueEvent.agentMessage">-->
<!--            智能体消息-->
<!--          </div>-->
<!--        </template>-->
<!--        <template #extra>-->
<!--          <div class="text-gray-500">{{ agent_thought.latency.toFixed(2) }}s</div>-->
<!--        </template>-->
<!--        <div-->
<!--          v-if="[QueueEvent.agentThought,QueueEvent.agentMessage].includes(agent_thought.event)"-->
<!--          class="text-xs text-gray-500 line-clamp-4 break-all"-->
<!--        >-->
<!--          {{ agent_thought.thought || '-' }}-->
<!--        </div>-->
<!--        <div v-else class="text-xs text-gray-500 line-clamp-4 break-all">-->
<!--          {{ agent_thought.observation || '-' }}-->
<!--        </div>-->
<!--      </a-collapse-item>-->
<!--    </a-collapse>-->
<!--  </div>-->
<!--</template>-->

<!--<style>-->
<!--.agent-thought {-->
<!--  .arco-collapse-item-content {-->
<!--    padding: 0 16px;-->
<!--  }-->
<!--}-->
<!--</style>-->
<script setup lang="ts">
import { type PropType, ref } from 'vue'
import { QueueEVENT,QueueEvent } from '@/config'

// 1.定义自定义组件所需数据
const props = defineProps({
  loading: { type: Boolean, default: false, required: true },
  agent_thoughts: {
    type: Array as PropType<Record<string, any>[]>,
    default: () => [],
    required: true,
  },
})
const visible = ref(false)

// 调试用：打印 agent_thoughts 数据
const debugAgentThoughts = () => {
  console.log('Agent Thoughts:', props.agent_thoughts)
  console.log('QueueEvent constants:', QueueEVENT)
  props.agent_thoughts.forEach((item, index) => {
    console.log(`Event ${index}:`, item.event, 'matches:', [
      QueueEVENT.longTermMemoryRecall,
      QueueEVENT.agentThought,
      QueueEVENT.datasetRetrieval,
      QueueEVENT.agentAction,
      QueueEVENT.agentMessage,
    ].includes(item.event))
  })
}
</script>

<template>
  <!-- 智能体推理步骤 -->
  <div :class="`flex flex-col rounded-2xl border ${visible ? 'w-[320px]' : 'w-[180px]'}`">
    <div
      :class="`flex items-center justify-between h-10 rounded-2xl bg-gray-100 px-4 text-gray-700 cursor-pointer w-auto ${visible ? 'rounded-bl-none rounded-br-none' : ''}`"
      @click="visible = !visible; debugAgentThoughts()"
    >
      <!-- 左侧图标与标题 -->
      <div class="flex items-center gap-2">
        <icon-list />
        {{ visible ? '隐藏' : '显示' }}运行流程
        <!-- 显示事件数量用于调试 -->
        <span class="text-xs bg-blue-100 px-1 rounded">
          {{ props.agent_thoughts.length }}
        </span>
      </div>
      <!-- 右侧图标 -->
      <div class="">
        <template v-if="props.loading">
          <icon-loading />
        </template>
        <template v-else>
          <icon-up v-if="visible" />
          <icon-down v-else />
        </template>
      </div>
    </div>

    <!-- 底部内容 -->
    <div v-if="visible" class="border-t">
      <!-- 如果没有事件数据，显示提示 -->
      <div v-if="props.agent_thoughts.length === 0" class="p-4 text-gray-500 text-sm">
        暂无运行流程数据
      </div>

      <!-- 显示所有事件（用于调试） -->
      <div v-else class="max-h-80 overflow-y-auto">
        <a-collapse class="agent-thought" destroy-on-hide :bordered="false">
          <a-collapse-item
            v-for="(agent_thought, index) in props.agent_thoughts.filter((item: any) =>
              [
                QueueEVENT.longTermMemoryRecall,
                QueueEVENT.agentThought,
                QueueEVENT.datasetRetrieval,
                QueueEVENT.agentAction,
                QueueEVENT.agentMessage,
              ].includes(item.event)
            )"
            :key="agent_thought.id || `thought-${index}`"
          >
            <template #expand-icon>
              <icon-file v-if="agent_thought.event === QueueEVENT.longTermMemoryRecall" />
              <icon-language v-else-if="agent_thought.event === QueueEVENT.agentThought" />
              <icon-storage v-else-if="agent_thought.event === QueueEVENT.datasetRetrieval" />
              <icon-tool v-else-if="agent_thought.event === QueueEVENT.agentAction" />
              <icon-message v-else-if="agent_thought.event === QueueEVENT.agentMessage" />
              <icon-info-circle v-else />
            </template>

            <template #header>
              <div class="flex items-center justify-between w-full">
                <div class="text-gray-700">
                  <span v-if="agent_thought.event === QueueEVENT.longTermMemoryRecall">长期记忆召回</span>
                  <span v-else-if="agent_thought.event === QueueEVENT.agentThought">智能体推理</span>
                  <span v-else-if="agent_thought.event === QueueEVENT.datasetRetrieval">搜索知识库</span>
                  <span v-else-if="agent_thought.event === QueueEVENT.agentAction">调用工具</span>
                  <span v-else-if="agent_thought.event === QueueEVENT.agentMessage">智能体消息</span>
                  <span v-else>{{ agent_thought.event || '未知事件' }}</span>
                </div>
                <div class="text-xs text-gray-400">
                  {{ agent_thought.event }}
                </div>
              </div>
            </template>

            <template #extra>
              <div class="text-gray-500 text-xs">
                {{ (agent_thought.latency || 0).toFixed(2) }}s
              </div>
            </template>

            <!-- 内容区域 -->
            <!-- 调试用：打印 agent_thoughts 数据 -->
            <div class="text-xs text-gray-500 break-all">
              <div v-if="['agent_thought',  'agent_message'].includes(agent_thought.event)">
                {{ agent_thought.thought || '-' }}
              </div>
              <div v-else>
                {{ agent_thought.observation || '-' }}
              </div>
            </div>
          </a-collapse-item>
        </a-collapse>
      </div>
    </div>
  </div>
</template>

<style>
.agent-thought {
  .arco-collapse-item-content {
    padding: 0 16px 16px 16px;
  }
  .arco-collapse-item-header {
    padding: 8px 16px;
  }
}
</style>