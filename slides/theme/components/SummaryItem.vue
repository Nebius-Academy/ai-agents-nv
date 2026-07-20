<script setup lang="ts">
defineProps<{
  number: string
  label: string
  detail?: string
}>()
</script>

<template>
  <div class="recap">
    <span>{{ number }}</span>
    <strong>{{ label }}</strong>
    <em v-if="detail">{{ detail }}</em>
  </div>
</template>
