<script setup lang="ts">
defineProps<{
  text?: string
}>()
</script>

<template>
  <div class="takeaway">
    <slot>{{ text }}</slot>
  </div>
</template>
