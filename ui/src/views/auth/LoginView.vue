<script setup lang="ts">
import LoginBanner from './components/LoginBanner.vue'
import LoginForm from './components/LoginForm.vue'
</script>

<template>
  <!-- 页面容器 -->
  <div class="flex h-screen bg-white">
    <!-- 顶部站点Logo -->
    <div class="fixed top-6 left-[22px] inline-flex items-center">
      <div class="bg-gray-100 h-8 leading-8 px-2 z-50">LLMOps AppBuilder</div>
    </div>
    <!-- 左侧banner -->
    <login-banner />
    <!-- 右侧表单 -->
    <div class="relative flex flex-1 items-center justify-center pb-10">
      <!-- 登录表单 -->
      <login-form />
      <!-- 底部footer -->
      <div class="absolute right-0 bottom-0 w-full">
        <footer class="flex items-center justify-center h-10 text-gray-600 text-center">
          LLMOps AppBuilder
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
