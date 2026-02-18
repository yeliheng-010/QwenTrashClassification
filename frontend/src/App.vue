<template>
  <router-view></router-view>
</template>

<style>
:root {
  --eco-green: #67C23A;
  --bg-gradient: linear-gradient(135deg, #e0f2f1 0%, #a5d6a7 100%);
  --category-kitchen: #8D6E63;
  --category-recyclable: #409EFF;
  --category-harmful: #F56C6C;
  --category-other: #909399;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-image: var(--bg-gradient);
  background-attachment: fixed;
  background-size: cover;
  min-height: 100vh;
}

/* 磨砂玻璃效果通用类 */
.glass-effect {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
  border-radius: 12px;
}
</style>
