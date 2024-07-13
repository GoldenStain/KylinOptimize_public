<template>
  <div class="hexagon-container">
    <div class="hexagon">
      <div class="content">
        <p class="title">{{ title }}</p>
        <div class="value">{{ content }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Hexagon',
  props: {
    content: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: true
    }
  }
}
</script>

<style scoped>
.hexagon-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  flex-direction: column;
  gap:10px;
}

.hexagon {
  position: relative;
  width: 120px;
  height: 120px;
  background-color: rgb(65, 114, 163);
  display: flex;
  justify-content: center;
  align-items: center;
  clip-path: polygon(50% 0%, 93% 25%, 93% 75%, 50% 100%, 7% 75%, 7% 25%);
}

.content {
  color: rgb(255, 252, 252);
  text-align: center;
}

.percentage {
  font-size: 20px;
}

.title {
  font-size: 16px;
  font-weight: bold;
}

.value {
  font-size: 24px;
  font-weight: bold;
}
</style>
