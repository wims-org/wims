<template>
  <main>
    <h1>Home</h1>
    <ul class="list-group block-item-list" data-testid="home-nav-list">
      <li class="list-group-item" @click="$router.push('/items')">Items</li>
      <li class="list-group-item" @click="$router.push('/categories')">Categories</li>
      <li class="list-group-item" @click="$router.push('/readers')">Readers</li>
      <li class="list-group-item" @click="$router.push('/import')">Import</li>
      <li class="list-group-item" @click="$router.push('/users')">Users</li>
    </ul>
    <ItemListContainer settingsId="home" title="Recent Items" />
  </main>
</template>

