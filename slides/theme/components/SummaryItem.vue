<script setup lang="ts">
defineProps<{
  number: string
  label: string
}>()
</script>

<template>
  <div class="recap">
    <span>{{ number }}</span>
    {{ label }}
  </div>
</template>
