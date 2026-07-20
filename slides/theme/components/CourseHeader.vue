<script setup lang="ts">
defineProps<{
  kicker: string
  title: string
}>()
</script>

<template>
  <header class="course-header">
    <div class="deck-kicker">{{ kicker }}</div>
    <h1>{{ title }}</h1>
  </header>
</template>
