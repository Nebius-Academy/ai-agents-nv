<script setup lang="ts">
defineProps<{
  number: string
  label: string
  title: string
  description: string
}>()
</script>

<template>
  <article class="flow-node">
    <div class="step">{{ number }} · {{ label }}</div>
    <strong>{{ title }}</strong>
    <p>{{ description }}</p>
  </article>
</template>
