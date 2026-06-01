<template>
  <main>
    <h1>Home</h1>
    <span class="instructions card p-3 mb-3" v-if="clientStore().showHomeInstructions">
      To create a new item:
      <ul>
        <li>
          <span class="link-badge badge text-bg-primary me-1" @click="$router.push('/readers')">Connect a reader
          </span>
          <font-awesome-icon icon="arrow-right" /> scan
        </li>
        <li>
          use your device's camera <font-awesome-icon icon="qrcode" /> scan a barcode or RFID tag
          <font-awesome-icon icon="arrow-right" /> open the item form with the code pre-filled
        </li>
        <li>
          <span class="link-badge badge text-bg-primary me-1" @click="$router.push('/items/new')">Manually
            create</span>an item without scanning
        </li>
      </ul>
      <BButton variant="primary" @click="clientStore().setShowHomeInstructions(false)">Dont show this again</BButton>
    </span>

    <ul class="list-group block-item-list" data-testid="home-nav-list">
      <div class="list-group-item p-0">
        <div class="d-flex align-items-center flex-wrap">
          <span class="list-group-item flex-fill p-3" @click="$router.push('/items')">Items</span>
          <span class="list-group-item p-3" @click.stop="$router.push('/items/new')">
            <font-awesome-icon icon="plus" />
            New Item
          </span>
        </div>
      </div>
      <li class="list-group-item" @click="$router.push('/categories')">Categories</li>
      <li class="list-group-item" @click="$router.push('/readers')">Readers</li>
      <li class="list-group-item" @click="$router.push('/import')">Import</li>
      <li class="list-group-item" @click="$router.push('/users')">Users</li>
    </ul>
    <ItemListContainer settingsId="home" title="Recent Items" :query="{ sort_desc: true, sort_by: 'created_at' }" />
  </main>
</template>

<script setup lang="ts">
import { clientStore } from '@/stores/clientStore'
</script>

<style scoped>
.instructions {
  cursor: default;
}

.link-badge {
  cursor: pointer;
}
</style>
