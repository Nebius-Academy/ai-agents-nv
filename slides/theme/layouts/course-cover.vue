<script setup lang="ts">
import nebLogo from '../assets/neb-logo.png'
</script>

<template>
  <div class="slidev-layout cover-slide">
    <img class="cover-logo" :src="nebLogo" alt="Nebius" />
    <div class="cover-copy">
      <slot />
    </div>
    <slot name="provider" />
    <div v-if="$slots.footer" class="cover-footer">
      <slot name="footer" />
    </div>
  </div>
</template>
