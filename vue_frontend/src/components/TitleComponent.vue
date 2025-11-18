<template>
  <BNavbar class="header" variant="primary" sticky="top">
    <BNavbar class="nav-container" fluid>
      <BNavbarBrand href="/">
        <img src="@/assets/icon.svg" alt="WIMS Logo" class="d-inline-block" height="50" />
        {{ msg }}</BNavbarBrand
      >
      <BCollapse id="nav-collapse" is-nav>
        <BNavbarNav >
          <BNavItemDropdown text="Functions" right hover>
            <BDropdownItem href="/items">Items</BDropdownItem>
            <BDropdownItem href="/readers">Readers</BDropdownItem>
            <BDropdownItem href="/users">Users</BDropdownItem>
            <BDropdownItem href="/about">About</BDropdownItem>
          </BNavItemDropdown>
          <BNavItemDropdown right>
            <!-- Using 'button-content' slot -->
            <template #button-content>
              <text v-if="user">{{ user?.username }}</text>
              <em v-else>User</em>
            </template>
            <BDropdownItem>Profile</BDropdownItem>
            <BDropdownItem>Sign Out</BDropdownItem>
          </BNavItemDropdown>
        </BNavbarNav>
      </BCollapse>

      <BNavbar v-b-color-mode="'dark'" variant="primary" class="ms-auto">
        <BNav>
          <BNavItem href="/readers">{{ connection_msg }}</BNavItem>
        </BNav>
        <BNavForm>
          <BFormInput class="me-sm-2" placeholder="Search" />
          <BButton variant="outline-success" class="my-2 my-sm-0" type="submit">Search</BButton>
        </BNavForm>
      </BNavbar>
    </BNavbar>
  </BNavbar>
</template>

<style scoped>
.header {
  align-items: center;
  background-color: var(--primary-bg-color);
  border-bottom: 1px solid var(--border-color);
  display: block;
  width: 100vw;
}

.header ::after {
  display: none;
}
.header .navbar-brand {
  font-weight: bold;
  font-size: 1.5rem;
}
.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding: 0;
  width: var(--content-max-width);
}

@media (max-width: var(--content-max-width)) {
  .nav-container {
    max-width: var(--content-max-width-small) !important;
    margin: 0 0 !important;
  }
}
</style>

<script setup lang="ts">
import { computed } from 'vue'
import { clientStore } from '@/stores/clientStore'
import { serverStream } from '@/stores/serverStream'

// State and Stores
const client_store = clientStore()
const server_stream = serverStream()
const msg = 'WIMS?!'

// Computed Properties

const connection_msg = computed(() => {
  if (connection_state.value === 0) {
    return `🟢 ${client_store.reader_id}`
  } else if (connection_state.value === 1) {
    return 'Connecting...'
  } else {
    return '🔴 Connect'
  }
})

const connection_state = computed(() => {
  if (
    server_stream.alive &&
    client_store?.reader_id.length > 0 &&
    client_store?.reader_id !== 'loading'
  ) {
    return 0 // Connected
  } else if (client_store?.reader_id.length > 0) {
    return 1 // Connecting
  } else {
    return 2 // Disconnected
  }
})

const user = computed(() => {
  return client_store.user
})
</script>
