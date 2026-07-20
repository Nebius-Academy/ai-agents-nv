<script setup lang="ts">
withDefaults(defineProps<{
  number?: string
  eyebrow?: string
  title: string
  description?: string
  items?: string[]
  badge?: string
  variant?: 'dark' | 'light' | 'lime'
}>(), {
  variant: 'dark',
  items: () => [],
})
</script>

<template>
  <article class="card compare-card" :class="variant">
    <div v-if="number" class="mega-icon">{{ number }}</div>
    <div v-if="eyebrow" class="eyebrow">{{ eyebrow }}</div>
    <h2>{{ title }}</h2>
    <p v-if="description">{{ description }}</p>
    <ul v-if="items.length">
      <li v-for="item in items" :key="item">{{ item }}</li>
    </ul>
    <div v-if="badge" class="pill" :class="{ ghost: variant === 'lime' }">{{ badge }}</div>
    <slot />
  </article>
</template>
