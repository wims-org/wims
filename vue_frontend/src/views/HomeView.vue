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
    <BTabs class="mt-4">
      <BTab title="New Items" active>
        <ItemListContainer settingsId="home" title="New Items" :query="{ sort_desc: true, sort_by: 'created_at' }" />
      </BTab>
      <BTab title="Low Stock">
        <ItemListContainer settingsId="home-low-stock" title="Low Stock Items"
          description="Items where amount is less than min_amount"
          :query="{ filters: [{ field: 'amount', qualifier: 'lt', value: 'min_amount' }], sort_by: 'amount', sort_desc: false }"
          :extraFields="['amount', 'min_amount']" />
      </BTab>
      <BTab title="Review Items">
        <ItemListContainer settingsId="home-review" title="Items Needing Review" description="Items with tag 'review'"
          :query="{ filters: [{ field: 'tags', qualifier: 'contains', value: 'review' }], sort_by: 'created_at', sort_desc: true }" />
      </BTab>
      <BTab title="Recently Updated">
        <ItemListContainer settingsId="home-recently-updated" title="Recently Updated Items"
          :query="{ sort_desc: true, sort_by: 'updated_at' }" />
      </BTab>
      <BTab title="Borrowed Items">
        <ItemListContainer settingsId="home-borrowed" title="Borrowed Items"
          :query="{ filters: [{ field: 'borrower_id', qualifier: 'not_eq', value: null }], sort_by: 'created_at', sort_desc: true }" />
      </BTab>
      <BTab title="Top Level Containers">
        <ItemListContainer settingsId="home-top-level-containers" title="Top Level Containers"
          description="Items with content that are not inside any other container" :query="{
            filters: [{ field: 'container_id', qualifier: 'eq', value: null },
            { field: 'content', qualifier: 'not_eq', value: null }], sort_by: 'created_at', sort_desc: true
          }" />
      </BTab>
    </BTabs>
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
