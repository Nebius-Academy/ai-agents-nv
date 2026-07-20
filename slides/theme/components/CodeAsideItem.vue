<script setup lang="ts">
defineProps<{
  label: string
  value?: string
}>()
</script>

<template>
  <div class="api-box">
    <div class="label">{{ label }}</div>
    <code><slot>{{ value }}</slot></code>
  </div>
</template>
