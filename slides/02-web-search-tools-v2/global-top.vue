<template>
  <div
    v-if="$nav.currentPage > 1 && $nav.currentPage < $nav.total"
    class="global-provider-row"
    aria-label="Course tools"
  >
    <span class="global-provider-label">Module 02</span>
    <span class="global-provider-rule" />
    <img class="global-tavily-logo" src="/tavily-logo.svg" alt="Tavily" />
    <span class="provider-plus">+</span>
    <img class="global-token-mark" src="/token-factory-mark.svg" alt="" />
    <span class="global-token-label">Nebius Token Factory</span>
  </div>
</template>
