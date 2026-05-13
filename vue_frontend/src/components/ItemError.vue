<template>
  <div class="d-flex flex-column align-items-center mt-5" data-testid="item-error">
    <p class="text-muted fs-5">The requested item was not found.</p>
    <router-link to="/items/new" class="btn btn-primary">Create new item</router-link>
  </div>
</template>

<script setup lang="ts"></script>
