<script setup lang="ts"></script>

<template>
  <main>
    <h1>Home</h1>
    <ul class="list-group block-item-list">
      <li class="list-group-item" @click="$router.push('/items')">Items</li>
      <li class="list-group-item" @click="$router.push('/readers')">Readers</li>
      <li class="list-group-item" @click="$router.push('/import')">Import</li>
    </ul>
  </main>
</template>
