<script setup lang="ts">
import BannerImage from '@/assets/images/login-banner.png'

// 轮播图列表
const carousels = [
  {
    slogan: '开箱即用的高质量AI编排模板',
    subSlogan: '丰富的应用组件，覆盖大多数典型业务场景',
    image: BannerImage,
  },
  {
    slogan: '零代码5分钟编排原生AI应用',
    subSlogan: '高效开发你的AI原生应用',
    image: BannerImage,
  },
]
</script>

<template>
  <div
    class="w-[550px] flex items-center justify-center bg-gradient-to-tr from-[#1d2129] to-[#00308f]"
  >
    <div class="flex-1 h-full">
      <a-carousel animation-name="fade" class="h-full">
        <a-carousel-item v-for="carousel in carousels" :key="carousel.slogan">
          <div class="flex flex-col items-center justify-center h-full">
            <div class="text-2xl leading-7 font-bold text-gray-100">{{ carousel.slogan }}</div>
            <div class="mt-2 text-gray-400 leading-[22px]">{{ carousel.subSlogan }}</div>
            <img :src="carousel.image" alt="LLMOps" class="w-[320px] mt-[30px]" />
          </div>
        </a-carousel-item>
      </a-carousel>
    </div>
  </div>
</template>

<style scoped></style>
