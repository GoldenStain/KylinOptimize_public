<template>
    <div class="numa-status-page">
      <h1>NUMA节点适配状态</h1>
      <div>
        <p>跨NUMA节点访问: {{ crossNuma ? '存在' : '不存在' }}</p>
        <div v-if="crossNuma">
          <h2>迁移状态</h2>
          <pre>{{ numadOutput }}</pre>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default{};
  </script>
<style scoped>
h1 {
  color: green;
  font-size: 24px;
}
p {
  color: green;
  font-size: 16px;
}
h2 {
  color: green;
  font-size: 20px;
  margin-top: 20px;
}
pre {
  background-color: #f8f8f8;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  white-space: pre-wrap; /* 保持换行符 */
  word-wrap: break-word; /* 长单词换行 */
  font-family: monospace;
  color: green;
}
</style>

