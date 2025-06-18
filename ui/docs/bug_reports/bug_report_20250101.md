# Bug Report - 2025年01月01日

## Bug 1: 知识库召回测试检索配置格式错乱

### 问题描述

在知识库召回测试模态窗中，选择 `检索配置` 时无法正常切换，只能使用默认的检索策略。

### 复现步骤

1. 找到知识库详情，点击 `召回测试`，选择 `检索设置`；
2. 从默认的 `相似性检索` 切换到 `其他检索方式`；
3. 无法正常切换，并且在点击 `召回测试` 时会发生错误。

### 影响范围

召回测试时无法切换到其他检索方式。

### 解决方案

在前面课时中，将 `reactive` 切换到 `ref` 时，`retrievalSettingForm` 未使用 `.value` 的形式获取数据，添加上即可修复。

```ts
// HitTestingModel.vue
const saveRetrievalSetting = () => {
    // 3.1 重置检索查询片段列表
    hitTestingSegments.value = []

    // 3.2 更新检索策略[修改的位置，将retrievalSettingForm修改为retrievalSettingForm.value]
    hitTestingForm.value = {query: hitTestingForm.value.query, ...retrievalSettingForm.value}

    // 3.3 隐藏模态窗
    retrievalSettingModalVisible.value = false
}
```