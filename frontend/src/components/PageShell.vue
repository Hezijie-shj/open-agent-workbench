<template>
  <AppHeader v-if="header" />
  <main :class="['page', compact ? 'page-compact' : '']">
    <slot />
  </main>
</template>

<script setup lang="ts">
import AppHeader from "./AppHeader.vue";

defineProps({
  header: {
    type: Boolean,
    default: true
  },
  compact: {
    type: Boolean,
    default: false
  }
});
</script>

