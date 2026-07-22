<template>
  <div
    v-if="$nav.currentPage > 1 && $nav.currentPage < $nav.total"
    class="global-course-footer"
    aria-label="Slide information"
  >
    <span>AI Agents · Module 02</span>
    <span class="page-number">{{ String($nav.currentPage).padStart(2, '0') }}</span>
  </div>
</template>
